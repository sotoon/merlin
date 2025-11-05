"""
Production-safe organizational structure import command.
NO DELETION OPERATIONS - Only creates/updates organizational entities.
Includes backup, rollback, validation, and detailed logging.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from api.management.commands._import_utils import open_csv, row_savepoint
from api.management.commands._prod_utils import ProductionImportBase
from api.models.organization import Department, Chapter, Tribe, Team, Organization
from api.models.user import User


class Command(BaseCommand):
    help = "PRODUCTION-SAFE: Import organizational entities from separate CSV files. NO DELETION - Only creates/updates entities."

    def add_arguments(self, parser):
        parser.add_argument("--csv", required=True, help="Path to CSV file (organizations.csv, chapters.csv, tribes.csv, or teams.csv)")
        parser.add_argument("--encoding", default="utf-8")
        parser.add_argument("--delimiter", default=",")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--log-file", default=None, help="Path to detailed log file")
        parser.add_argument("--backup", action="store_true", default=True, help="Create backup before import")
        parser.add_argument("--create-users", action="store_true", help="Create users if they don't exist when referenced by email")
        parser.add_argument("--force-update", action="store_true", help="Force update existing organizational relationships")
        parser.add_argument("--validate", action="store_true", default=True, help="Validate data after import")

    def handle(self, *args, **options):
        csv_path = options["csv"]
        encoding = options["encoding"]
        delimiter = options["delimiter"]
        dry_run = bool(options["dry_run"])
        log_file = options.get("log_file")
        create_backup = bool(options["backup"])
        create_users = bool(options["create_users"])
        force_update = bool(options["force_update"])
        validate = bool(options["validate"])

        # Initialize production import utilities
        prod_import = ProductionImportBase(self, log_file)
        
        # Start production import with safety measures
        if not prod_import.start_production_import("org_structure_import", create_backup):
            raise CommandError("Failed to start production import")

        try:
            # Determine which type of file we're processing based on the filename or columns
            filename = csv_path.split('/')[-1].lower()
            if 'organizations' in filename:
                file_type = 'organizations'
            elif 'chapters' in filename:
                file_type = 'chapters'
            elif 'tribes' in filename:
                file_type = 'tribes'
            elif 'teams' in filename:
                file_type = 'teams'
            else:
                # Try to detect from first row columns
                try:
                    first_row = next(open_csv(csv_path, encoding=encoding, delimiter=delimiter))
                    if 'organization_name' in first_row:
                        file_type = 'organizations'
                    elif 'chapter_name' in first_row:
                        file_type = 'chapters'
                    elif 'tribe_name' in first_row:
                        file_type = 'tribes'
                    elif 'team_name' in first_row:
                        file_type = 'teams'
                    else:
                        raise CommandError("Could not determine file type from filename or columns")
                except:
                    raise CommandError("Could not determine file type from filename or columns")

            created = updated = skipped = users_created = 0
            errors = []

            with transaction.atomic():
                for idx, row in enumerate(open_csv(csv_path, encoding=encoding, delimiter=delimiter), start=2):
                    with row_savepoint(dry_run):
                        try:
                            if file_type == 'organizations':
                                result = self._process_organization(row, idx, prod_import, dry_run)
                                created += result.get('created', 0)
                                updated += result.get('updated', 0)
                                skipped += result.get('skipped', 0)

                            elif file_type == 'chapters':
                                result = self._process_chapter(row, idx, prod_import, dry_run, create_users)
                                created += result.get('created', 0)
                                updated += result.get('updated', 0)
                                skipped += result.get('skipped', 0)
                                users_created += result.get('users_created', 0)

                            elif file_type == 'tribes':
                                result = self._process_tribe(row, idx, prod_import, dry_run, create_users)
                                created += result.get('created', 0)
                                updated += result.get('updated', 0)
                                skipped += result.get('skipped', 0)
                                users_created += result.get('users_created', 0)

                            elif file_type == 'teams':
                                result = self._process_team(row, idx, prod_import, dry_run, create_users, force_update)
                                created += result.get('created', 0)
                                updated += result.get('updated', 0)
                                skipped += result.get('skipped', 0)
                                users_created += result.get('users_created', 0)

                        except Exception as e:
                            errors.append(f"Row {idx}: {str(e)}")
                            prod_import.logger.log_operation(
                                "org_entity_processing_failed",
                                {"row": idx, "file_type": file_type, "error": str(e)},
                                "error"
                            )
                
                if dry_run:
                    transaction.set_rollback(True)
                    self.stdout.write(self.style.WARNING("Dry-run complete (no changes committed)."))
            
            if not dry_run:
                # Complete production import with validation
                if validate:
                    expected_counts = {
                        "org_entities": created + updated,
                        "users_created": users_created
                    }
                    
                    if not prod_import.complete_production_import("org_structure", expected_counts):
                        self.stdout.write(self.style.ERROR("Import completed but validation failed. Check logs for details."))
                        return

            # Final summary
            message = f"PRODUCTION-SAFE Org import finished. created={created}, updated={updated}, skipped={skipped}"
            if users_created > 0:
                message += f", users_created={users_created}"
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
                "org_import_failed",
                {"error": str(e)},
                "error"
            )
            self.stdout.write(self.style.ERROR(f"Import failed: {str(e)}"))
            
            if prod_import.backup_path:
                self.stdout.write("Backup available for rollback if needed")
            
            raise CommandError(f"Production import failed: {str(e)}")

    def _process_organization(self, row, idx, prod_import, dry_run):
        """PRODUCTION-SAFE: Process organization creation/update."""
        org_name = (row.get("organization_name") or "").strip()
        if not org_name:
            return {"skipped": 1}
        
        if not dry_run:
            org, org_created = Organization.objects.update_or_create(
                name=org_name, 
                defaults={}
            )
            
            if org_created:
                prod_import.logger.log_operation(
                    "organization_created",
                    {"name": org_name}
                )
                return {"created": 1}
            else:
                prod_import.logger.log_operation(
                    "organization_already_exists",
                    {"name": org_name}
                )
                return {"updated": 1}
        
        return {"created": 1}

    def _process_chapter(self, row, idx, prod_import, dry_run, create_users):
        """PRODUCTION-SAFE: Process chapter creation/update."""
        chap_name = (row.get("chapter_name") or "").strip()
        chap_desc = (row.get("chapter_description") or "").strip()
        chap_leader_email = (row.get("chapter_leader_email") or "").strip()

        if not chap_name:
            return {"skipped": 1}

        if not dry_run:
            # Get or create leader user (PRODUCTION-SAFE: Only create, no deletion)
            leader = None
            users_created = 0
            if chap_leader_email:
                leader = self._get_or_create_user_prod(chap_leader_email, create_users, dry_run, prod_import)
                if leader and hasattr(leader, 'id') and leader.id:
                    users_created = 1

            # Link chapter to Engineering department by default (PRODUCTION-SAFE: Only create, no deletion)
            eng_dep = Department.objects.filter(name="Engineering").first()
            if not eng_dep:
                eng_dep, _ = Department.objects.get_or_create(name="Engineering")
                prod_import.logger.log_operation(
                    "department_created",
                    {"name": "Engineering"}
                )

            chapter, chapter_created = Chapter.objects.update_or_create(
                name=chap_name,
                defaults={
                    "department": eng_dep,
                    "leader": leader,
                    "description": chap_desc,
                },
            )
            
            if chapter_created:
                prod_import.logger.log_operation(
                    "chapter_created",
                    {"name": chap_name, "leader": chap_leader_email}
                )
                return {"created": 1, "users_created": users_created}
            else:
                prod_import.logger.log_operation(
                    "chapter_updated",
                    {"name": chap_name, "leader": chap_leader_email}
                )
                return {"updated": 1, "users_created": users_created}
        
        return {"created": 1}

    def _process_tribe(self, row, idx, prod_import, dry_run, create_users):
        """PRODUCTION-SAFE: Process tribe creation/update."""
        tribe_name = (row.get("tribe_name") or "").strip()
        tribe_desc = (row.get("tribe_description") or "").strip()
        tribe_category_raw = (row.get("tribe_category") or "").strip()
        tribe_eng_director_email = (row.get("tribe_engineering_director_email") or "").strip()
        tribe_prod_director_email = (row.get("tribe_product_director_email") or "").strip()
        
        if not tribe_name:
            return {"skipped": 1}

        if not dry_run:
            # Normalize category to uppercase (PRODUCTION-SAFE: Only update, no deletion)
            if tribe_category_raw:
                category_lower = tribe_category_raw.lower()
                if "non" in category_lower or "غیر" in category_lower:
                    tribe_category = "NON_TECH"
                else:
                    tribe_category = "TECH"
            else:
                tribe_category = None

            # Link tribe to Engineering department by default (PRODUCTION-SAFE: Only create, no deletion)
            eng_dep = Department.objects.filter(name="Engineering").first()
            if not eng_dep:
                eng_dep, _ = Department.objects.get_or_create(name="Engineering")
                prod_import.logger.log_operation(
                    "department_created",
                    {"name": "Engineering"}
                )

            # Get or create directors (PRODUCTION-SAFE: Only create, no deletion)
            eng_director = None
            prod_director = None
            users_created = 0
            
            if tribe_eng_director_email:
                eng_director = self._get_or_create_user_prod(tribe_eng_director_email, create_users, dry_run, prod_import)
                if eng_director and hasattr(eng_director, 'id') and eng_director.id:
                    users_created += 1
            
            if tribe_prod_director_email:
                prod_director = self._get_or_create_user_prod(tribe_prod_director_email, create_users, dry_run, prod_import)
                if prod_director and hasattr(prod_director, 'id') and prod_director.id:
                    users_created += 1

            tribe, tribe_created = Tribe.objects.update_or_create(
                name=tribe_name,
                defaults={
                    "department": eng_dep,
                    "category": tribe_category or None,
                    "description": tribe_desc,
                    "engineering_director": eng_director,
                    "product_director": prod_director,
                },
            )
            
            if tribe_created:
                prod_import.logger.log_operation(
                    "tribe_created",
                    {"name": tribe_name, "category": tribe_category}
                )
                return {"created": 1, "users_created": users_created}
            else:
                prod_import.logger.log_operation(
                    "tribe_updated",
                    {"name": tribe_name, "category": tribe_category}
                )
                return {"updated": 1, "users_created": users_created}
        
        return {"created": 1}

    def _process_team(self, row, idx, prod_import, dry_run, create_users, force_update):
        """PRODUCTION-SAFE: Process team creation/update."""
        team_name = (row.get("team_name") or "").strip()
        team_desc = (row.get("team_description") or "").strip()
        team_tribe_name = (row.get("team_tribe_name") or "").strip()
        team_category_raw = (row.get("team_category") or "").strip()
        team_leader_email = (row.get("team_leader_email") or "").strip()

        if not team_name:
            return {"skipped": 1}

        if not dry_run:
            # Normalize category to uppercase (PRODUCTION-SAFE: Only update, no deletion)
            team_category = team_category_raw.upper() if team_category_raw else None
            if team_category and team_category not in ["TECH", "NON_TECH"]:
                if team_category == "NON-TECH":
                    team_category = "NON_TECH"
                else:
                    team_category = "TECH" if "tech" in team_category_raw.lower() else "NON_TECH"

            # Get or create tribe (PRODUCTION-SAFE: Only create, no deletion)
            t_tribe = None
            if team_tribe_name:
                t_tribe, _ = Tribe.objects.get_or_create(name=team_tribe_name)
                if not t_tribe.id:  # Newly created
                    prod_import.logger.log_operation(
                        "tribe_created_for_team",
                        {"tribe": team_tribe_name, "team": team_name}
                    )

            # Get or create leader user (PRODUCTION-SAFE: Only create, no deletion)
            leader = None
            users_created = 0
            if team_leader_email:
                leader = self._get_or_create_user_prod(team_leader_email, create_users, dry_run, prod_import)
                if leader and hasattr(leader, 'id') and leader.id:
                    users_created = 1

            # Determine appropriate department (PRODUCTION-SAFE: Only create, no deletion)
            if t_tribe and t_tribe.category == "NON_TECH":
                dep_name = t_tribe.name
            elif team_category == "NON_TECH":
                dep_name = team_name
            else:
                dep_name = "Engineering"

            # Get or create the department (PRODUCTION-SAFE: Only create, no deletion)
            dep, dep_created = Department.objects.get_or_create(name=dep_name)
            if dep_created:
                prod_import.logger.log_operation(
                    "department_created_for_team",
                    {"department": dep_name, "team": team_name}
                )

            team, team_created = Team.objects.update_or_create(
                name=team_name,
                defaults={
                    "department": dep,
                    "tribe": t_tribe,
                    "category": team_category or None,
                    "leader": leader,
                    "description": team_desc,
                },
            )
            
            if team_created:
                prod_import.logger.log_operation(
                    "team_created",
                    {"name": team_name, "tribe": team_tribe_name, "category": team_category}
                )
                return {"created": 1, "users_created": users_created}
            else:
                prod_import.logger.log_operation(
                    "team_updated",
                    {"name": team_name, "tribe": team_tribe_name, "category": team_category}
                )
                return {"updated": 1, "users_created": users_created}
        
        return {"created": 1}

    def _get_or_create_user_prod(self, email, create_users, dry_run, prod_import):
        """PRODUCTION-SAFE: Get existing user or create new one if create_users is True and not dry-run."""
        if not email:
            return None

        user = User.objects.filter(email=email).first()
        if user:
            return user

        if not create_users or dry_run:
            prod_import.logger.log_operation(
                "user_not_created",
                {"email": email, "reason": "create_users=False or dry_run=True"},
                "warning"
            )
            return None

        # Create new user with minimal required fields (PRODUCTION-SAFE: Only create, no deletion)
        try:
            user = User.objects.create(
                email=email,
                username=email,  # Required field
                name=email.split('@')[0] if '@' in email else email,  # Use part before @ as name
                is_active=True,
            )
            prod_import.logger.log_operation(
                "user_created_for_org",
                {"email": email, "name": user.name}
            )
            return user
        except Exception as e:
            prod_import.logger.log_operation(
                "user_creation_failed",
                {"email": email, "error": str(e)},
                "error"
            )
            return None
