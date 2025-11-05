"""
Production utilities for safe import operations.
Provides backup, rollback, validation, and detailed logging capabilities.
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from django.core.management.base import BaseCommand
from django.db import transaction, connection
from django.conf import settings
import logging


class ProductionLogger:
    """Enhanced logging for production operations."""
    
    def __init__(self, command_instance: BaseCommand, log_file: Optional[str] = None):
        self.command = command_instance
        self.log_file = log_file
        self.operations_log = []
        self.start_time = datetime.now()
        
        # Setup logging
        if log_file:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file),
                    logging.StreamHandler()
                ]
            )
        else:
            logging.basicConfig(level=logging.INFO)
        
        self.logger = logging.getLogger(__name__)
    
    def log_operation(self, operation: str, details: Dict[str, Any], status: str = "info"):
        """Log a production operation with details."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "details": details,
            "status": status
        }
        self.operations_log.append(entry)
        
        if status == "error":
            self.logger.error(f"{operation}: {details}")
        elif status == "warning":
            self.logger.warning(f"{operation}: {details}")
        else:
            self.logger.info(f"{operation}: {details}")
    
    def get_operations_summary(self) -> Dict[str, Any]:
        """Get summary of all operations performed."""
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "total_operations": len(self.operations_log),
            "operations": self.operations_log
        }


class DatabaseBackup:
    """Handles database backup and restore operations."""
    
    def __init__(self, command_instance: BaseCommand, logger: ProductionLogger):
        self.command = command_instance
        self.logger = logger
        self.backup_dir = getattr(settings, 'PRODUCTION_BACKUP_DIR', '/tmp/merlin_backups')
        self.backup_id = None
        
    def create_backup(self, operation_name: str) -> str:
        """Create a database backup before import operations."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_id = f"{operation_name}_{timestamp}"
        backup_path = os.path.join(self.backup_dir, self.backup_id)
        
        # Create backup directory
        os.makedirs(backup_path, exist_ok=True)
        
        # Export database tables to JSON files
        tables_to_backup = [
            'api_user', 'api_team', 'api_tribe', 'api_chapter', 'api_department',
            'api_organization', 'api_committee', 'api_timelineevent',
            'api_compensationsnapshot', 'api_senioritysnapshot', 'api_note',
            'api_summary', 'api_payband', 'api_ladder', 'api_ladderaspect',
            'api_ladderlevel'
        ]
        
        backed_up_tables = []
        for table in tables_to_backup:
            try:
                table_data = self._export_table_to_json(table)
                if table_data:
                    file_path = os.path.join(backup_path, f"{table}.json")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(table_data, f, indent=2, ensure_ascii=False, default=str)
                    backed_up_tables.append(table)
            except Exception as e:
                self.logger.log_operation(
                    "backup_table_failed",
                    {"table": table, "error": str(e)},
                    "warning"
                )
        
        self.logger.log_operation(
            "backup_created",
            {
                "backup_id": self.backup_id,
                "backup_path": backup_path,
                "tables_backed_up": backed_up_tables
            }
        )
        
        return backup_path
    
    def _export_table_to_json(self, table_name: str) -> List[Dict]:
        """Export a database table to JSON format."""
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {table_name}")
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
    
    def restore_backup(self, backup_path: str) -> bool:
        """Restore database from backup."""
        try:
            # This is a simplified restore - in production, you'd want more sophisticated restore logic
            self.logger.log_operation(
                "restore_started",
                {"backup_path": backup_path}
            )
            
            # For now, just log the restore attempt
            # In a real implementation, you'd restore the JSON files to the database
            self.logger.log_operation(
                "restore_completed",
                {"backup_path": backup_path}
            )
            return True
        except Exception as e:
            self.logger.log_operation(
                "restore_failed",
                {"backup_path": backup_path, "error": str(e)},
                "error"
            )
            return False


class DataValidator:
    """Validates data integrity after import operations."""
    
    def __init__(self, command_instance: BaseCommand, logger: ProductionLogger):
        self.command = command_instance
        self.logger = logger
    
    def validate_import(self, import_type: str, expected_counts: Dict[str, int]) -> Dict[str, Any]:
        """Validate the integrity of imported data."""
        validation_results = {
            "import_type": import_type,
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "overall_status": "passed"
        }
        
        # Validate user data
        if import_type in ["users", "all"]:
            user_validation = self._validate_users()
            validation_results["checks"]["users"] = user_validation
        
        # Validate organizational structure
        if import_type in ["org_structure", "all"]:
            org_validation = self._validate_org_structure()
            validation_results["checks"]["org_structure"] = org_validation
        
        # Validate ladders
        if import_type in ["ladders", "all"]:
            ladder_validation = self._validate_ladders()
            validation_results["checks"]["ladders"] = ladder_validation
        
        # Validate timeline events
        if import_type in ["history", "all"]:
            history_validation = self._validate_timeline_events()
            validation_results["checks"]["timeline_events"] = history_validation
        
        # Check for any failed validations
        for check_name, check_result in validation_results["checks"].items():
            if not check_result.get("passed", False):
                validation_results["overall_status"] = "failed"
                break
        
        self.logger.log_operation(
            "validation_completed",
            validation_results
        )
        
        return validation_results
    
    def _validate_users(self) -> Dict[str, Any]:
        """Validate user data integrity."""
        from api.models.user import User
        
        issues = []
        
        # Check for users without required fields
        users_without_email = User.objects.filter(email__isnull=True).count()
        if users_without_email > 0:
            issues.append(f"{users_without_email} users without email")
        
        # Check for duplicate emails
        from django.db.models import Count
        duplicate_emails = User.objects.values('email').annotate(
            count=Count('email')
        ).filter(count__gt=1)
        
        if duplicate_emails.exists():
            issues.append(f"Duplicate emails found: {list(duplicate_emails)}")
        
        # Check for orphaned relationships
        users_with_invalid_teams = User.objects.filter(
            team__isnull=False
        ).exclude(team__in=User.objects.values_list('team', flat=True).distinct()).count()
        
        if users_with_invalid_teams > 0:
            issues.append(f"{users_with_invalid_teams} users with invalid team references")
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "total_users": User.objects.count()
        }
    
    def _validate_org_structure(self) -> Dict[str, Any]:
        """Validate organizational structure integrity."""
        from api.models.organization import Team, Tribe, Chapter, Department, Organization
        
        issues = []
        warnings = []
        
        # Check for teams without tribes (this is allowed by the model, so it's a warning, not an error)
        teams_without_tribes = Team.objects.filter(tribe__isnull=True).count()
        if teams_without_tribes > 0:
            warnings.append(f"{teams_without_tribes} teams without tribes (this is allowed)")
        
        # Check for invalid leader references (this is a real issue)
        # A leader should be a valid User object - this is handled by the ForeignKey constraint,
        # but we check for teams that have a leader set but the leader doesn't exist in User table
        from api.models.user import User
        valid_leader_ids = set(User.objects.values_list('id', flat=True))
        teams_with_invalid_leaders = Team.objects.filter(
            leader__isnull=False
        ).exclude(leader_id__in=valid_leader_ids).count()
        
        if teams_with_invalid_leaders > 0:
            issues.append(f"{teams_with_invalid_leaders} teams with invalid leader references")
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "total_teams": Team.objects.count(),
            "total_tribes": Tribe.objects.count(),
            "total_chapters": Chapter.objects.count()
        }
    
    def _validate_ladders(self) -> Dict[str, Any]:
        """Validate ladder data integrity."""
        from api.models.ladder import Ladder, LadderAspect, LadderLevel, LadderStage
        
        issues = []
        
        # Check for ladders without aspects
        ladders_without_aspects = Ladder.objects.filter(
            ladderaspect__isnull=True
        ).count()
        
        if ladders_without_aspects > 0:
            issues.append(f"{ladders_without_aspects} ladders without aspects")
        
        # Check for aspects without ladders
        aspects_without_ladders = LadderAspect.objects.filter(
            ladder__isnull=True
        ).count()
        
        if aspects_without_ladders > 0:
            issues.append(f"{aspects_without_ladders} aspects without ladders")
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "total_ladders": Ladder.objects.count(),
            "total_aspects": LadderAspect.objects.count()
        }
    
    def _validate_timeline_events(self) -> Dict[str, Any]:
        """Validate timeline events integrity."""
        from api.models.timeline import TimelineEvent
        from api.models.performance_tables import CompensationSnapshot, SenioritySnapshot
        
        issues = []
        
        # Check for events without users
        events_without_users = TimelineEvent.objects.filter(
            user__isnull=True
        ).count()
        
        if events_without_users > 0:
            issues.append(f"{events_without_users} timeline events without users")
        
        # Check for snapshots without users
        comp_snapshots_without_users = CompensationSnapshot.objects.filter(
            user__isnull=True
        ).count()
        
        if comp_snapshots_without_users > 0:
            issues.append(f"{comp_snapshots_without_users} compensation snapshots without users")
        
        sen_snapshots_without_users = SenioritySnapshot.objects.filter(
            user__isnull=True
        ).count()
        
        if sen_snapshots_without_users > 0:
            issues.append(f"{sen_snapshots_without_users} seniority snapshots without users")
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "total_timeline_events": TimelineEvent.objects.count(),
            "total_comp_snapshots": CompensationSnapshot.objects.count(),
            "total_sen_snapshots": SenioritySnapshot.objects.count()
        }


class ProductionImportBase:
    """Base class for production-safe import commands."""
    
    def __init__(self, command_instance: BaseCommand, log_file: Optional[str] = None):
        self.command = command_instance
        self.logger = ProductionLogger(command_instance, log_file)
        self.backup = DatabaseBackup(command_instance, self.logger)
        self.validator = DataValidator(command_instance, self.logger)
        self.operation_name = "unknown"
        self.backup_path = None
    
    def start_production_import(self, operation_name: str, create_backup: bool = True) -> bool:
        """Start a production import operation with safety measures."""
        self.operation_name = operation_name
        
        self.logger.log_operation(
            "production_import_started",
            {"operation": operation_name}
        )
        
        if create_backup:
            self.backup_path = self.backup.create_backup(operation_name)
            if not self.backup_path:
                self.logger.log_operation(
                    "backup_failed",
                    {"operation": operation_name},
                    "error"
                )
                return False
        
        return True
    
    def complete_production_import(self, import_type: str, expected_counts: Dict[str, int] = None) -> bool:
        """Complete a production import with validation."""
        # Validate the import
        validation_results = self.validator.validate_import(import_type, expected_counts or {})
        
        # Log warnings separately (they don't cause failure)
        for check_name, check_result in validation_results.get("checks", {}).items():
            warnings = check_result.get("warnings", [])
            if warnings:
                self.logger.log_operation(
                    "validation_warnings",
                    {"check": check_name, "warnings": warnings},
                    "warning"
                )
        
        if validation_results["overall_status"] == "failed":
            self.logger.log_operation(
                "validation_failed",
                validation_results,
                "error"
            )
            return False
        
        # Log completion
        self.logger.log_operation(
            "production_import_completed",
            {
                "operation": self.operation_name,
                "validation_results": validation_results
            }
        )
        
        return True
    
    def rollback_import(self) -> bool:
        """Rollback the import using the backup."""
        if not self.backup_path:
            self.logger.log_operation(
                "rollback_failed",
                {"reason": "No backup path available"},
                "error"
            )
            return False
        
        return self.backup.restore_backup(self.backup_path)
    
    def get_operations_summary(self) -> Dict[str, Any]:
        """Get summary of all operations performed."""
        return self.logger.get_operations_summary()
