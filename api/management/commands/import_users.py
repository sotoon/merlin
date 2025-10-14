import csv
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.auth.hashers import make_password

from api.management.commands._import_utils import open_csv, row_savepoint
from api.models.user import User
from api.models.organization import Department, Chapter, Tribe, Team, Organization, Committee
from api.models.role import Role, RoleType, RoleScope


class Command(BaseCommand):
    help = "Import users from CSV file. Clears existing users (except superusers) and creates new ones with roles."

    def add_arguments(self, parser):
        parser.add_argument("--csv", required=True, help="Path to users CSV file")
        parser.add_argument("--encoding", default="utf-8")
        parser.add_argument("--delimiter", default=",")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--clear-users", action="store_true", help="Clear existing users before import")

    def handle(self, *args, **options):
        csv_path = options["csv"]
        encoding = options["encoding"]
        delimiter = options["delimiter"]
        dry_run = bool(options["dry_run"])
        clear_users = bool(options["clear_users"])

        # Clear existing users if requested (except superusers)
        if clear_users and not dry_run:
            self.stdout.write("Clearing existing data...")

            # Clear related data first (in reverse dependency order)
            from api.models.performance_tables import CompensationSnapshot, SenioritySnapshot
            from api.models.timeline import TimelineEvent
            from api.models.organization import Committee

            # Delete compensation snapshots
            comp_count = CompensationSnapshot.objects.all().delete()[0]
            self.stdout.write(f"Deleted {comp_count} compensation snapshots")

            # Delete seniority snapshots
            sen_count = SenioritySnapshot.objects.all().delete()[0]
            self.stdout.write(f"Deleted {sen_count} seniority snapshots")

            # Delete timeline events
            tl_count = TimelineEvent.objects.all().delete()[0]
            self.stdout.write(f"Deleted {tl_count} timeline events")

            # Clear organizational relationships that reference users
            Committee.objects.all().delete()
            self.stdout.write("Cleared committees")

            # Clear leader references in organizational entities
            Team.objects.filter(leader__isnull=False).update(leader=None)
            Chapter.objects.filter(leader__isnull=False).update(leader=None)
            Tribe.objects.filter(product_director__isnull=False).update(product_director=None)
            Tribe.objects.filter(engineering_director__isnull=False).update(engineering_director=None)
            Organization.objects.filter(cto__isnull=False).update(cto=None)
            Organization.objects.filter(cpo__isnull=False).update(cpo=None)
            Organization.objects.filter(hr_manager__isnull=False).update(hr_manager=None)
            Organization.objects.filter(maintainer__isnull=False).update(maintainer=None)
            Organization.objects.filter(ceo__isnull=False).update(ceo=None)
            Organization.objects.filter(vp__isnull=False).update(vp=None)
            Organization.objects.filter(cfo__isnull=False).update(cfo=None)
            Organization.objects.filter(sales_manager__isnull=False).update(sales_manager=None)

            self.stdout.write("Cleared organizational leader references")

            # Now delete users (except superusers)
            deleted_count = User.objects.filter(is_superuser=False).delete()[0]
            self.stdout.write(f"Deleted {deleted_count} users")

        created = updated = skipped = users_with_roles = 0

        # PASS 1: Create all users first without relationships
        with transaction.atomic():
            for idx, row in enumerate(open_csv(csv_path, encoding=encoding, delimiter=delimiter), start=2):
                with row_savepoint(dry_run):
                    # Extract user data
                    name = (row.get("Name") or "").strip()
                    email = (row.get("Email") or "").strip()
                    gmail = (row.get("Gmail") or "").strip()
                    phone = (row.get("Phone") or "").strip() if "Phone" in row else ""
                    role_name = (row.get("Role") or "").strip()

                    if not email:
                        skipped += 1
                        continue

                    # Create or get user
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
                        else:
                            updated += 1

                        # Set password for all users
                        user.set_password("pw")
                        user.save(update_fields=["password"])
                        
                        if role_name:
                            users_with_roles += 1

        # PASS 2: Set organizational assignments and relationships
        with transaction.atomic():
            for idx, row in enumerate(open_csv(csv_path, encoding=encoding, delimiter=delimiter), start=2):
                with row_savepoint(dry_run):
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
                        continue

                    # Set organizational assignments (team takes precedence over tribe)
                    organization = Organization.objects.first()  # Use the first organization
                    team_obj = None
                    tribe_obj = None
                    chapter_obj = None
                    department_obj = None

                    if team_name:
                        team_obj = Team.objects.filter(name=team_name).first()
                        if team_obj:
                            # Set team
                            user.team = team_obj
                            department_obj = team_obj.department
                            
                            # Tribe comes from team automatically (via property)
                            # Get chapter from team's tribe's department if available
                            if team_obj.tribe and team_obj.tribe.department:
                                chapter_obj = Chapter.objects.filter(department=team_obj.tribe.department).first()
                    
                    elif tribe_name:
                        tribe_obj = Tribe.objects.filter(name=tribe_name).first()
                        if tribe_obj:
                            # No team, just tribe
                            user.team = None
                            department_obj = tribe_obj.department

                    # Set all organizational fields
                    user.chapter = None  # Clear chapter for all users
                    user.department = department_obj  # Set department properly from team/tribe
                    user.organization = organization
                    user.save(update_fields=["team", "chapter", "department", "organization"])

                    # Set leader relationship
                    if leader_email:
                        leader = User.objects.filter(email=leader_email).first()
                        if leader:
                            user.leader = leader
                            user.save(update_fields=["leader"])

                    # Set agile coach
                    if agile_coach_email:
                        agile_coach = User.objects.filter(email=agile_coach_email).first()
                        if agile_coach:
                            user.agile_coach = agile_coach
                            user.save(update_fields=["agile_coach"])

                    # Assign roles
                    if role_name:
                        self._assign_user_role(user, role_name)

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry-run complete (no changes committed)."))
        message = f"Users import finished. created={created}, updated={updated}, skipped={skipped}"
        if users_with_roles > 0:
            message += f", users_with_roles={users_with_roles}"
        self.stdout.write(self.style.SUCCESS(message))

    def _assign_user_role(self, user, role_name):
        """Assign a role to a user by setting them as the role holder on appropriate organizational entities"""
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
            self.stderr.write(f"Warning: Unknown role '{role_name}' for user {user.email}")
            return

        # Determine which organizational entity to assign the role to
        if field_name in ["cto", "vp", "ceo", "cpo", "hr_manager", "cfo", "sales_manager"]:
            # Organization-level roles
            org = Organization.objects.first()  # Use the first (and likely only) organization
            if org:
                setattr(org, field_name, user)
                org.save(update_fields=[field_name])
                self.stdout.write(f"Assigned {role_name} role to {user.email} on organization")

        elif field_name in ["engineering_director", "product_director"]:
            # Tribe-level roles - assign to user's tribe if they have one
            if user.tribe:
                setattr(user.tribe, field_name, user)
                user.tribe.save(update_fields=[field_name])
                self.stdout.write(f"Assigned {role_name} role to {user.email} on tribe {user.tribe.name}")
            else:
                self.stderr.write(f"Warning: Cannot assign {role_name} role to {user.email} - no tribe assigned")

        # Create a committee for the role (for UI purposes)
        committee_name = f"{role_name} Committee"
        committee, committee_created = Committee.objects.get_or_create(
            name=committee_name,
            defaults={"description": f"Committee for {role_name} role"}
        )

        # Add user to committee for UI visibility
        if not committee.members.filter(pk=user.pk).exists():
            committee.members.add(user)

        # Set user's committee reference for easy access
        user.committee = committee
        user.save(update_fields=["committee"])
