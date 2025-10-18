from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from api.management.commands._import_utils import open_csv, row_savepoint
from api.models.organization import Department, Chapter, Tribe, Team, Organization
from api.models.user import User


class Command(BaseCommand):
    help = "Import organizational entities from separate CSV files. Creates users if they don't exist when referenced by email."

    def add_arguments(self, parser):
        parser.add_argument("--csv", required=True, help="Path to CSV file (organizations.csv, chapters.csv, tribes.csv, or teams.csv)")
        parser.add_argument("--encoding", default="utf-8")
        parser.add_argument("--delimiter", default=",")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--create-users", action="store_true", help="Create users if they don't exist when referenced by email")

    def handle(self, *args, **options):
        # Django passes dest names without leading dashes
        csv_path = options["csv"]
        encoding = options["encoding"]
        delimiter = options["delimiter"]
        dry_run = bool(options["dry_run"])
        create_users = bool(options["create_users"])

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

        with transaction.atomic():
            for idx, row in enumerate(open_csv(csv_path, encoding=encoding, delimiter=delimiter), start=2):
                with row_savepoint(dry_run):

                    if file_type == 'organizations':
                        # Process organizations
                        org_name = (row.get("organization_name") or "").strip()
                        if org_name:
                            org, org_created = Organization.objects.update_or_create(name=org_name, defaults={})
                            created += 1 if org_created else 0
                            updated += 0 if org_created else 1

                            # Create default departments for this organization
                            # Since we don't have department data in the CSV, we'll create them based on common patterns
                            default_deps = ["Engineering", "Product", "Operations", "Administration"]
                            for dep_name in default_deps:
                                dep, dep_created = Department.objects.update_or_create(
                                    name=dep_name,
                                    defaults={}
                                )
                                if dep_created:
                                    created += 1
                                else:
                                    updated += 1

                    elif file_type == 'chapters':
                        # Process chapters
                        chap_name = (row.get("chapter_name") or "").strip()
                        chap_desc = (row.get("chapter_description") or "").strip()
                        chap_leader_email = (row.get("chapter_leader_email") or "").strip()

                        if chap_name:
                            # Get or create leader user
                            leader = None
                            if chap_leader_email:
                                leader = self._get_or_create_user(chap_leader_email, create_users, dry_run)
                                if leader and not dry_run and leader.id:
                                    users_created += 1

                            # Link chapter to Engineering department by default (since we don't have department info in CSV)
                            eng_dep = Department.objects.filter(name="Engineering").first()
                            if not eng_dep:
                                # Create Engineering department if it doesn't exist
                                eng_dep, _ = Department.objects.get_or_create(name="Engineering")

                            chapter, chapter_created = Chapter.objects.update_or_create(
                                name=chap_name,
                                defaults={
                                    "department": eng_dep,
                                    "leader": leader,
                                    "description": chap_desc,
                                },
                            )
                            created += 1 if chapter_created else 0
                            updated += 0 if chapter_created else 1

                    elif file_type == 'tribes':
                        # Process tribes
                        tribe_name = (row.get("tribe_name") or "").strip()
                        tribe_desc = (row.get("tribe_description") or "").strip()
                        tribe_category_raw = (row.get("tribe_category") or "").strip()
                        tribe_eng_director_email = (row.get("tribe_engineering_director_email") or "").strip()
                        tribe_prod_director_email = (row.get("tribe_product_director_email") or "").strip()
                        
                        # Normalize category to uppercase
                        if tribe_category_raw:
                            category_lower = tribe_category_raw.lower()
                            if "non" in category_lower or "غیر" in category_lower:
                                tribe_category = "NON_TECH"
                            else:
                                tribe_category = "TECH"
                        else:
                            tribe_category = None

                        if tribe_name:
                            # Link tribe to Engineering department by default (since we don't have department info in CSV)
                            eng_dep = Department.objects.filter(name="Engineering").first()
                            if not eng_dep:
                                # Create Engineering department if it doesn't exist
                                eng_dep, _ = Department.objects.get_or_create(name="Engineering")

                            # Get or create engineering director
                            eng_director = None
                            if tribe_eng_director_email:
                                eng_director = self._get_or_create_user(tribe_eng_director_email, create_users, dry_run)
                                if eng_director and not dry_run and hasattr(eng_director, 'id') and eng_director.id:
                                    users_created += 1
                            
                            # Get or create product director
                            prod_director = None
                            if tribe_prod_director_email:
                                prod_director = self._get_or_create_user(tribe_prod_director_email, create_users, dry_run)
                                if prod_director and not dry_run and hasattr(prod_director, 'id') and prod_director.id:
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
                            created += 1 if tribe_created else 0
                            updated += 0 if tribe_created else 1

                    elif file_type == 'teams':
                        # Process teams
                        team_name = (row.get("team_name") or "").strip()
                        team_desc = (row.get("team_description") or "").strip()
                        team_tribe_name = (row.get("team_tribe_name") or "").strip()
                        team_category_raw = (row.get("team_category") or "").strip()
                        # Normalize category to uppercase
                        team_category = team_category_raw.upper() if team_category_raw else None
                        if team_category and team_category not in ["TECH", "NON_TECH"]:
                            # Handle "NON-TECH" -> "NON_TECH"
                            if team_category == "NON-TECH":
                                team_category = "NON_TECH"
                            else:
                                team_category = "TECH" if "tech" in team_category_raw.lower() else "NON_TECH"
                        team_leader_email = (row.get("team_leader_email") or "").strip()

                        if team_name:
                            # Get or create tribe
                            t_tribe = None
                            if team_tribe_name:
                                t_tribe, _ = Tribe.objects.get_or_create(name=team_tribe_name)

                            # Get or create leader user
                            leader = None
                            if team_leader_email:
                                leader = self._get_or_create_user(team_leader_email, create_users, dry_run)
                                if leader and not dry_run and leader.id:
                                    users_created += 1

                            # Determine appropriate department based on tribe category or team name
                            if t_tribe and t_tribe.category == "NON_TECH":
                                # For non-tech tribes, use tribe name as department
                                dep_name = t_tribe.name
                            elif team_category == "NON_TECH":
                                # For non-tech teams, use team name as department
                                dep_name = team_name
                            else:
                                # Default to Engineering for tech teams
                                dep_name = "Engineering"

                            # Get or create the department
                            dep, _ = Department.objects.get_or_create(name=dep_name)

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
                            created += 1 if team_created else 0
                            updated += 0 if team_created else 1

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry-run complete (no changes committed)."))
        message = f"Org import finished. created={created}, updated={updated}, skipped={skipped}"
        if users_created > 0:
            message += f", users_created={users_created}"
        self.stdout.write(self.style.SUCCESS(message))

    def _get_or_create_user(self, email, create_users, dry_run):
        """Get existing user or create new one if create_users is True and not dry-run"""
        if not email:
            return None

        user = User.objects.filter(email=email).first()
        if user:
            return user

        if not create_users or dry_run:
            return None

        # Create new user with minimal required fields
        try:
            user = User.objects.create(
                email=email,
                username=email,  # Required field
                name=email.split('@')[0] if '@' in email else email,  # Use part before @ as name
                is_active=True,
            )
            return user
        except Exception as e:
            self.stderr.write(f"Warning: Could not create user {email}: {e}")
            return None


