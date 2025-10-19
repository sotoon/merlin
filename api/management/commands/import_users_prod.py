"""
Production-safe user import command.
NO DELETION OPERATIONS - Only creates/updates users and relationships.
Includes backup, rollback, validation, and detailed logging.
"""

import csv
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.auth.hashers import make_password

from api.management.commands._import_utils import open_csv, row_savepoint
from api.management.commands._prod_utils import ProductionImportBase
from api.models.user import User
from api.models.organization import Department, Chapter, Tribe, Team, Organization, Committee
from api.models.role import Role, RoleType, RoleScope


class Command(BaseCommand):
    help = "PRODUCTION-SAFE: Import users from CSV file. NO DELETION - Only creates/updates users and relationships."

    def add_arguments(self, parser):
        parser.add_argument("--csv", required=True, help="Path to users CSV file")
        parser.add_argument("--encoding", default="utf-8")
        parser.add_argument("--delimiter", default=",")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--log-file", default=None, help="Path to detailed log file")
        parser.add_argument("--backup", action="store_true", default=True, help="Create backup before import")
        parser.add_argument("--force-update", action="store_true", help="Force update existing user relationships")
        parser.add_argument("--validate", action="store_true", default=True, help="Validate data after import")

    def handle(self, *args, **options):
        csv_path = options["csv"]
        encoding = options["encoding"]
        delimiter = options["delimiter"]
        dry_run = bool(options["dry_run"])
        log_file = options.get("log_file")
        create_backup = bool(options["backup"])
        force_update = bool(options["force_update"])
        validate = bool(options["validate"])

        # Initialize production import utilities
        prod_import = ProductionImportBase(self, log_file)
        
        # Start production import with safety measures
        if not prod_import.start_production_import("user_import", create_backup):
            raise CommandError("Failed to start production import")

        try:
            created = updated = skipped = users_with_roles = 0
            errors = []

            # PASS 1: Create/update all users first without relationships
            with transaction.atomic():
                for idx, row in enumerate(open_csv(csv_path, encoding=encoding, delimiter=delimiter), start=2):
                    with row_savepoint(dry_run):
                        try:
                            # Extract user data
                            name = (row.get("Name") or "").strip()
                            email = (row.get("Email") or "").strip()
                            gmail = (row.get("Gmail") or "").strip()
                            phone = (row.get("Phone") or "").strip() if "Phone" in row else ""
                            role_name = (row.get("Role") or "").strip()

                            if not email:
                                skipped += 1
                                prod_import.logger.log_operation(
                                    "user_skipped",
                                    {"row": idx, "reason": "No email provided"},
                                    "warning"
                                )
                                continue

                            # Create or get user (PRODUCTION-SAFE: No deletion)
                            if not dry_run:
                                user, user_created = User.objects.update_or_create(
                                    email=email,
                                    defaults={
                                        "name": name,
                                        "gmail": gmail,
                                        "phone": phone,
                                        "username": email,
                                        "is_active": True,
                                    }
                                )

                                if user_created:
                                    created += 1
                                    prod_import.logger.log_operation(
                                        "user_created",
                                        {"email": email, "name": name}
                                    )
                                else:
                                    updated += 1
                                    prod_import.logger.log_operation(
                                        "user_updated",
                                        {"email": email, "name": name}
                                    )
                                
                                if role_name:
                                    users_with_roles += 1

                        except Exception as e:
                            errors.append(f"Row {idx}: {str(e)}")
                            prod_import.logger.log_operation(
                                "user_creation_failed",
                                {"row": idx, "email": email, "error": str(e)},
                                "error"
                            )

            # PASS 2: Set organizational assignments and relationships (PRODUCTION-SAFE)
            with transaction.atomic():
                for idx, row in enumerate(open_csv(csv_path, encoding=encoding, delimiter=delimiter), start=2):
                    with row_savepoint(dry_run):
                        try:
                            email = (row.get("Email") or "").strip()
                            team_name = (row.get("Team") or "").strip()
                            tribe_name = (row.get("Tribe") or "").strip()
                            leader_email = (row.get("Leader") or "").strip()
                            agile_coach_email = (row.get("PR") or "").strip() or (row.get("Agile Coach") or "").strip()
                            role_name = (row.get("Role") or "").strip()

                            if not email:
                                continue

                            if dry_run:
                                continue

                            user = User.objects.filter(email=email).first()
                            if not user:
                                prod_import.logger.log_operation(
                                    "user_not_found",
                                    {"email": email, "row": idx},
                                    "warning"
                                )
                                continue

                            # Update organizational assignments (PRODUCTION-SAFE: Only update, no deletion)
                            organization = Organization.objects.first()  # Use the first organization
                            team_obj = None
                            tribe_obj = None
                            chapter_obj = None
                            department_obj = None

                            if team_name:
                                team_obj = Team.objects.filter(name=team_name).first()
                                if team_obj:
                                    # Update team assignment
                                    if user.team != team_obj or force_update:
                                        user.team = team_obj
                                        department_obj = team_obj.department
                                        
                                        # Tribe comes from team automatically (via property)
                                        # Get chapter from team's tribe's department if available
                                        if team_obj.tribe and team_obj.tribe.department:
                                            chapter_obj = Chapter.objects.filter(department=team_obj.tribe.department).first()
                                        
                                        prod_import.logger.log_operation(
                                            "team_assignment_updated",
                                            {"user": email, "team": team_name}
                                        )
                                else:
                                    prod_import.logger.log_operation(
                                        "team_not_found",
                                        {"user": email, "team": team_name},
                                        "warning"
                                    )
                            
                            elif tribe_name:
                                tribe_obj = Tribe.objects.filter(name=tribe_name).first()
                                if tribe_obj:
                                    # Update tribe assignment (no team)
                                    if user.team != None or force_update:
                                        user.team = None
                                        department_obj = tribe_obj.department
                                        
                                        prod_import.logger.log_operation(
                                            "tribe_assignment_updated",
                                            {"user": email, "tribe": tribe_name}
                                        )
                                else:
                                    prod_import.logger.log_operation(
                                        "tribe_not_found",
                                        {"user": email, "tribe": tribe_name},
                                        "warning"
                                    )

                            # Update organizational fields (PRODUCTION-SAFE: Only update, no deletion)
                            if force_update or user.chapter != chapter_obj or user.department != department_obj:
                                user.chapter = chapter_obj  # Update chapter assignment
                                user.department = department_obj  # Update department assignment
                                user.organization = organization
                                user.save(update_fields=["team", "chapter", "department", "organization"])
                                
                                prod_import.logger.log_operation(
                                    "org_fields_updated",
                                    {"user": email, "chapter": chapter_obj.name if chapter_obj else None, "department": department_obj.name if department_obj else None}
                                )

                            # Update leader relationship (PRODUCTION-SAFE: Only update, no deletion)
                            if leader_email:
                                leader = User.objects.filter(email=leader_email).first()
                                if leader:
                                    if user.leader != leader or force_update:
                                        user.leader = leader
                                        user.save(update_fields=["leader"])
                                        
                                        prod_import.logger.log_operation(
                                            "leader_assignment_updated",
                                            {"user": email, "leader": leader_email}
                                        )
                                else:
                                    prod_import.logger.log_operation(
                                        "leader_not_found",
                                        {"user": email, "leader": leader_email},
                                        "warning"
                                    )

                            # Update agile coach (PRODUCTION-SAFE: Only update, no deletion)
                            if agile_coach_email:
                                agile_coach = User.objects.filter(email=agile_coach_email).first()
                                if agile_coach:
                                    if user.agile_coach != agile_coach or force_update:
                                        user.agile_coach = agile_coach
                                        user.save(update_fields=["agile_coach"])
                                        
                                        prod_import.logger.log_operation(
                                            "agile_coach_assignment_updated",
                                            {"user": email, "agile_coach": agile_coach_email}
                                        )
                                else:
                                    prod_import.logger.log_operation(
                                        "agile_coach_not_found",
                                        {"user": email, "agile_coach": agile_coach_email},
                                        "warning"
                                    )

                            # Assign roles (PRODUCTION-SAFE: Only update, no deletion)
                            if role_name:
                                self._assign_user_role_prod(user, role_name, prod_import)

                        except Exception as e:
                            errors.append(f"Row {idx} (relationships): {str(e)}")
                            prod_import.logger.log_operation(
                                "relationship_update_failed",
                                {"row": idx, "email": email, "error": str(e)},
                                "error"
                            )

            if dry_run:
                transaction.set_rollback(True)
                self.stdout.write(self.style.WARNING("Dry-run complete (no changes committed)."))
            else:
                # Complete production import with validation
                if validate:
                    expected_counts = {
                        "users": created + updated,
                        "users_with_roles": users_with_roles
                    }
                    
                    if not prod_import.complete_production_import("users", expected_counts):
                        self.stdout.write(self.style.ERROR("Import completed but validation failed. Check logs for details."))
                        return

            # Final summary
            message = f"PRODUCTION-SAFE Users import finished. created={created}, updated={updated}, skipped={skipped}"
            if users_with_roles > 0:
                message += f", users_with_roles={users_with_roles}"
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
                "import_failed",
                {"error": str(e)},
                "error"
            )
            self.stdout.write(self.style.ERROR(f"Import failed: {str(e)}"))
            
            if prod_import.backup_path:
                self.stdout.write("Backup available for rollback if needed")
            
            raise CommandError(f"Production import failed: {str(e)}")

    def _assign_user_role_prod(self, user, role_name, prod_import):
        """PRODUCTION-SAFE: Assign a role to a user by setting them as the role holder on appropriate organizational entities."""
        from api.models.organization import Organization, Tribe

        # Map role names to the field names on organizational entities
        role_field_mapping = {
            "Engineering Director": "engineering_director",  # On Tribe
            "CFO": "cfo",  # On Organization
            "Sales Manager": "sales_manager",  # On Organization
            "CEO": "ceo",  # On Organization
            "CTO": "cto",  # On Organization
            "VP": "vp",  # On Organization
            "CPO": "cpo",  # On Organization
            "HR Manager": "hr_manager",  # On Organization
            "Product Director": "product_director",  # On Tribe
        }

        field_name = role_field_mapping.get(role_name)
        if not field_name:
            prod_import.logger.log_operation(
                "unknown_role",
                {"user": user.email, "role": role_name},
                "warning"
            )
            return

        try:
            # Determine which organizational entity to assign the role to
            if field_name in ["cto", "vp", "ceo", "cpo", "hr_manager", "cfo", "sales_manager"]:
                # Organization-level roles (PRODUCTION-SAFE: Only update, no deletion)
                org = Organization.objects.first()  # Use the first (and likely only) organization
                if org:
                    current_holder = getattr(org, field_name, None)
                    if current_holder != user:  # Only update if different
                        setattr(org, field_name, user)
                        org.save(update_fields=[field_name])
                        
                        prod_import.logger.log_operation(
                            "org_role_assigned",
                            {"user": user.email, "role": role_name, "organization": org.name}
                        )
                    else:
                        prod_import.logger.log_operation(
                            "org_role_already_assigned",
                            {"user": user.email, "role": role_name}
                        )

            elif field_name in ["engineering_director", "product_director"]:
                # Tribe-level roles - assign to user's tribe if they have one (PRODUCTION-SAFE)
                if user.tribe:
                    current_holder = getattr(user.tribe, field_name, None)
                    if current_holder != user:  # Only update if different
                        setattr(user.tribe, field_name, user)
                        user.tribe.save(update_fields=[field_name])
                        
                        prod_import.logger.log_operation(
                            "tribe_role_assigned",
                            {"user": user.email, "role": role_name, "tribe": user.tribe.name}
                        )
                    else:
                        prod_import.logger.log_operation(
                            "tribe_role_already_assigned",
                            {"user": user.email, "role": role_name, "tribe": user.tribe.name}
                        )
                else:
                    prod_import.logger.log_operation(
                        "tribe_role_assignment_skipped",
                        {"user": user.email, "role": role_name, "reason": "No tribe assigned"},
                        "warning"
                    )

            # Create or update committee for the role (PRODUCTION-SAFE: Only create/update, no deletion)
            committee_name = f"{role_name} Committee"
            committee, committee_created = Committee.objects.get_or_create(
                name=committee_name,
                defaults={"description": f"Committee for {role_name} role"}
            )

            # Add user to committee for UI visibility (PRODUCTION-SAFE: Only add, no removal)
            if not committee.members.filter(pk=user.pk).exists():
                committee.members.add(user)
                prod_import.logger.log_operation(
                    "user_added_to_committee",
                    {"user": user.email, "committee": committee_name}
                )

            # Update user's committee reference (PRODUCTION-SAFE: Only update, no deletion)
            if user.committee != committee:
                user.committee = committee
                user.save(update_fields=["committee"])
                
                prod_import.logger.log_operation(
                    "user_committee_updated",
                    {"user": user.email, "committee": committee_name}
                )

        except Exception as e:
            prod_import.logger.log_operation(
                "role_assignment_failed",
                {"user": user.email, "role": role_name, "error": str(e)},
                "error"
            )
