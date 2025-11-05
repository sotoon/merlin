"""
Production-safe ladders import command.
NO DELETION OPERATIONS - Only creates/updates ladder entities.
Includes backup, rollback, validation, and detailed logging.
"""

from typing import Optional
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from api.management.commands._import_utils import (
    average_or_none,
    normalize_stage,
    open_csv,
    row_savepoint,
)
from api.management.commands._prod_utils import ProductionImportBase
from api.models.ladder import Ladder, LadderAspect, LadderLevel, LadderStage


class Command(BaseCommand):
    help = "PRODUCTION-SAFE: Import ladders, aspects, or levels from separate CSV files. NO DELETION - Only creates/updates entities."

    def add_arguments(self, parser):
        parser.add_argument("--csv", required=True, help="Absolute path to CSV file")
        parser.add_argument("--encoding", default="utf-8")
        parser.add_argument("--delimiter", default=",")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--log-file", default=None, help="Path to detailed log file")
        parser.add_argument("--backup", action="store_true", default=True, help="Create backup before import")
        parser.add_argument("--ladders-only", action="store_true", help="Import only ladders section")
        parser.add_argument("--aspects-only", action="store_true", help="Import only aspects section")
        parser.add_argument("--levels-only", action="store_true", help="Import only levels section")
        parser.add_argument("--force-update", action="store_true", help="Force update existing ladder entities")
        parser.add_argument("--validate", action="store_true", default=True, help="Validate data after import")

    def handle(self, *args, **options):
        csv_path = options["csv"]
        encoding = options["encoding"]
        delimiter = options["delimiter"]
        dry_run = bool(options["dry_run"])
        log_file = options.get("log_file")
        create_backup = bool(options["backup"])
        ladders_only = bool(options["ladders_only"])
        aspects_only = bool(options["aspects_only"])
        levels_only = bool(options["levels_only"])
        force_update = bool(options["force_update"])
        validate = bool(options["validate"])

        # Initialize production import utilities
        prod_import = ProductionImportBase(self, log_file)
        
        # Start production import with safety measures
        if not prod_import.start_production_import("ladders_import", create_backup):
            raise CommandError("Failed to start production import")

        try:
            created = updated = skipped = 0
            errors = []

            with transaction.atomic():
                for idx, row in enumerate(open_csv(csv_path, encoding=encoding, delimiter=delimiter), start=2):
                    with row_savepoint(dry_run):
                        try:
                            # Determine what to import based on flags and CSV content
                            if ladders_only or self._is_ladder_row(row):
                                result = self._process_ladder(row, idx, prod_import, dry_run, force_update)
                                created += result.get('created', 0)
                                updated += result.get('updated', 0)
                                skipped += result.get('skipped', 0)

                            elif aspects_only or self._is_aspect_row(row):
                                result = self._process_aspect(row, idx, prod_import, dry_run, force_update)
                                created += result.get('created', 0)
                                updated += result.get('updated', 0)
                                skipped += result.get('skipped', 0)

                            elif levels_only or self._is_level_row(row):
                                result = self._process_level(row, idx, prod_import, dry_run, force_update)
                                created += result.get('created', 0)
                                updated += result.get('updated', 0)
                                skipped += result.get('skipped', 0)

                            else:
                                skipped += 1
                                prod_import.logger.log_operation(
                                    "row_skipped",
                                    {"row": idx, "reason": "Could not determine row type"},
                                    "warning"
                                )

                        except Exception as e:
                            errors.append(f"Row {idx}: {str(e)}")
                            prod_import.logger.log_operation(
                                "ladder_entity_processing_failed",
                                {"row": idx, "error": str(e)},
                                "error"
                            )
                
                if dry_run:
                    transaction.set_rollback(True)
                    self.stdout.write(self.style.WARNING("Dry-run complete (no changes committed)."))
            
            if not dry_run:
                # Complete production import with validation
                if validate:
                    expected_counts = {
                        "ladder_entities": created + updated
                    }
                    
                    if not prod_import.complete_production_import("ladders", expected_counts):
                        self.stdout.write(self.style.ERROR("Import completed but validation failed. Check logs for details."))
                        return

            # Final summary
            message = f"PRODUCTION-SAFE Ladders import finished. created={created}, updated={updated}, skipped={skipped}"
            if errors:
                message += f", errors={len(errors)}"
                self.stdout.write(self.style.WARNING(f"Errors encountered: {errors}"))
            
            self.stdout.write(self.style.SUCCESS(message))
            
            # Log operations summary
            operations_summary = prod_import.get_operations_summary()
            self.stdout.write(f"Operations performed: {operations_summary['total_operations']}")
            
            if prod_import.backup_path:
                self.stdout.write(f"Backup created at: {prod_import.backup_path}")
                self.stdout.write("Use --rollback flag to restore from backup if needed")

        except Exception as e:
            prod_import.logger.log_operation(
                "ladders_import_failed",
                {"error": str(e)},
                "error"
            )
            self.stdout.write(self.style.ERROR(f"Import failed: {str(e)}"))
            
            if prod_import.backup_path:
                self.stdout.write("Backup available for rollback if needed")
            
            raise CommandError(f"Production import failed: {str(e)}")

    def _is_ladder_row(self, row):
        """Check if row contains ladder data."""
        return any(key in row for key in ['ladder_code', 'ladder_name', 'ladder_title'])

    def _is_aspect_row(self, row):
        """Check if row contains aspect data."""
        return any(key in row for key in ['aspect_code', 'aspect_name', 'aspect_title'])

    def _is_level_row(self, row):
        """Check if row contains level data."""
        return any(key in row for key in ['level_number', 'level_name', 'level_title'])

    def _process_ladder(self, row, idx, prod_import, dry_run, force_update):
        """PRODUCTION-SAFE: Process ladder creation/update."""
        ladder_code = (row.get("ladder_code") or "").strip()
        ladder_name = (row.get("ladder_name") or row.get("ladder_title") or "").strip()
        ladder_description = (row.get("ladder_description") or "").strip()

        if not ladder_code or not ladder_name:
            return {"skipped": 1}

        if not dry_run:
            ladder, ladder_created = Ladder.objects.update_or_create(
                code=ladder_code,
                defaults={
                    "name": ladder_name,
                    "description": ladder_description,
                }
            )
            
            if ladder_created:
                prod_import.logger.log_operation(
                    "ladder_created",
                    {"code": ladder_code, "name": ladder_name}
                )
                return {"created": 1}
            else:
                prod_import.logger.log_operation(
                    "ladder_updated",
                    {"code": ladder_code, "name": ladder_name}
                )
                return {"updated": 1}
        
        return {"created": 1}

    def _process_aspect(self, row, idx, prod_import, dry_run, force_update):
        """PRODUCTION-SAFE: Process aspect creation/update."""
        aspect_code = (row.get("aspect_code") or "").strip()
        aspect_name = (row.get("aspect_name") or row.get("aspect_title") or "").strip()
        aspect_description = (row.get("aspect_description") or "").strip()
        ladder_code = (row.get("ladder_code") or "").strip()

        if not aspect_code or not aspect_name or not ladder_code:
            return {"skipped": 1}

        if not dry_run:
            # Get the ladder (PRODUCTION-SAFE: Only get, no deletion)
            ladder = Ladder.objects.filter(code=ladder_code).first()
            if not ladder:
                prod_import.logger.log_operation(
                    "ladder_not_found_for_aspect",
                    {"aspect_code": aspect_code, "ladder_code": ladder_code},
                    "warning"
                )
                return {"skipped": 1}

            aspect, aspect_created = LadderAspect.objects.update_or_create(
                code=aspect_code,
                ladder=ladder,
                defaults={
                    "name": aspect_name,
                    "description": aspect_description,
                }
            )
            
            if aspect_created:
                prod_import.logger.log_operation(
                    "aspect_created",
                    {"code": aspect_code, "name": aspect_name, "ladder": ladder_code}
                )
                return {"created": 1}
            else:
                prod_import.logger.log_operation(
                    "aspect_updated",
                    {"code": aspect_code, "name": aspect_name, "ladder": ladder_code}
                )
                return {"updated": 1}
        
        return {"created": 1}

    def _process_level(self, row, idx, prod_import, dry_run, force_update):
        """PRODUCTION-SAFE: Process level creation/update."""
        level_number = (row.get("level_number") or "").strip()
        level_name = (row.get("level_name") or row.get("level_title") or "").strip()
        level_description = (row.get("level_description") or "").strip()
        ladder_code = (row.get("ladder_code") or "").strip()

        if not level_number or not level_name or not ladder_code:
            return {"skipped": 1}

        if not dry_run:
            try:
                level_num = float(level_number)
            except ValueError:
                prod_import.logger.log_operation(
                    "invalid_level_number",
                    {"level_number": level_number, "level_name": level_name},
                    "warning"
                )
                return {"skipped": 1}

            # Get the ladder (PRODUCTION-SAFE: Only get, no deletion)
            ladder = Ladder.objects.filter(code=ladder_code).first()
            if not ladder:
                prod_import.logger.log_operation(
                    "ladder_not_found_for_level",
                    {"level_number": level_number, "ladder_code": ladder_code},
                    "warning"
                )
                return {"skipped": 1}

            level, level_created = LadderLevel.objects.update_or_create(
                number=level_num,
                ladder=ladder,
                defaults={
                    "name": level_name,
                    "description": level_description,
                }
            )
            
            if level_created:
                prod_import.logger.log_operation(
                    "level_created",
                    {"number": level_num, "name": level_name, "ladder": ladder_code}
                )
                return {"created": 1}
            else:
                prod_import.logger.log_operation(
                    "level_updated",
                    {"number": level_num, "name": level_name, "ladder": ladder_code}
                )
                return {"updated": 1}
        
        return {"created": 1}
