"""
Fix duplicate users created due to case-sensitive email matching in import_users_prod.

⚠️  SAFETY: This command ONLY deletes users created on the specified date/time.
⚠️  It will NEVER delete old/existing users - only the problematic duplicates.

This command:
1. Finds duplicate users (case-insensitive email match) created on a specific date
2. Transfers all related data from duplicates to originals (timeline events, snapshots, etc.)
3. Deletes ONLY the duplicate users created on that specific date

⚠️  IMPORTANT: This command does NOT update the original users' data fields.
   After running this, you must run 'import_users_prod' again to update
   the original users' name, email, gmail, phone, and organizational assignments.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from datetime import datetime
import pytz

from api.models.user import User
from api.models.timeline import TimelineEvent, Notice, StockGrant, TitleChange
from api.models.performance_tables import (
    OrgAssignmentSnapshot,
    CompensationSnapshot,
    SenioritySnapshot,
    DataAccessOverride,
)
from api.models.note import Note, Summary, Feedback
from api.models.activity import OneOnOneActivityLog
from api.models.form import Form, FormAssignment


class Command(BaseCommand):
    help = "Fix duplicate users created due to case-sensitive email matching"

    def add_arguments(self, parser):
        parser.add_argument(
            "--date",
            required=True,
            help="Date when duplicates were created (format: YYYY-MM-DD HH:MM, e.g., '2025-11-06 10:12')",
        )
        parser.add_argument(
            "--exclude-email",
            default="arash.rahimi@sotoon.ir",
            help="Email to exclude from deletion (default: arash.rahimi@sotoon.ir)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be done without making changes",
        )
        parser.add_argument(
            "--timezone",
            default="Asia/Tehran",
            help="Timezone for date parsing (default: Asia/Tehran)",
        )

    def handle(self, *args, **options):
        date_str = options["date"]
        exclude_email = options["exclude_email"].lower()
        dry_run = options["dry_run"]
        tz_name = options["timezone"]

        # Parse the date
        try:
            tz = pytz.timezone(tz_name)
            # Parse date string (format: "2025-11-06 10:12" or "2025-11-06")
            if " " in date_str:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
            else:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                # Default to 10:12 if not provided
                date_obj = date_obj.replace(hour=10, minute=12)
            
            # Make it timezone-aware
            date_obj = tz.localize(date_obj)
            # Convert to UTC for database comparison
            date_obj_utc = date_obj.astimezone(pytz.UTC)
        except ValueError as e:
            raise CommandError(f"Invalid date format: {e}. Expected: YYYY-MM-DD HH:MM or YYYY-MM-DD")

        self.stdout.write(f"Looking for users created on: {date_obj} ({date_obj_utc} UTC)")
        self.stdout.write(f"Excluding: {exclude_email}")

        # Find all users created on that date (within a 1-minute window to account for processing time)
        from django.utils import timezone
        start_time = date_obj_utc
        end_time = date_obj_utc.replace(second=59)
        
        candidates = User.objects.filter(
            date_created__gte=start_time,
            date_created__lte=end_time,
        ).exclude(email__iexact=exclude_email)

        self.stdout.write(f"\nFound {candidates.count()} candidate users created in that time window")

        # Group by case-insensitive email
        email_groups = {}
        for user in candidates:
            email_lower = user.email.lower()
            if email_lower not in email_groups:
                email_groups[email_lower] = []
            email_groups[email_lower].append(user)

        # Find duplicates (groups with more than one user)
        duplicates_found = {email: users for email, users in email_groups.items() if len(users) > 1}
        
        if not duplicates_found:
            self.stdout.write(self.style.SUCCESS("No duplicate users found!"))
            return

        self.stdout.write(f"\nFound {len(duplicates_found)} duplicate email groups:")
        for email, users in duplicates_found.items():
            self.stdout.write(f"  {email}: {len(users)} users")
            for user in users:
                self.stdout.write(f"    - {user.email} (ID: {user.id}, created: {user.date_created})")

        if dry_run:
            self.stdout.write(self.style.WARNING("\nDRY RUN - No changes will be made"))
            return

        # Process each duplicate group
        total_fixed = 0
        total_deleted = 0

        # SAFETY CHECK: Verify we're only working with users from the target date
        self.stdout.write(self.style.WARNING(
            f"\n⚠️  SAFETY CHECK: Only users created between {start_time} and {end_time} UTC will be processed."
        ))
        self.stdout.write(self.style.WARNING(
            "⚠️  NO OLD USERS WILL BE DELETED - Only duplicates from the specified date/time window."
        ))

        with transaction.atomic():
            for email_lower, users in duplicates_found.items():
                # Determine original (prefer lowercase email, then oldest)
                original = None
                duplicates = []

                # Sort by email (lowercase first) then by creation date
                users_sorted = sorted(users, key=lambda u: (u.email.lower() != email_lower, u.date_created))

                original = users_sorted[0]
                duplicates = users_sorted[1:]

                self.stdout.write(f"\nProcessing {email_lower}:")
                self.stdout.write(f"  Original (KEEPING): {original.email} (ID: {original.id}, created: {original.date_created})")
                for dup in duplicates:
                    # SAFETY CHECK: Verify duplicate was created in the target time window
                    if not (start_time <= dup.date_created <= end_time):
                        self.stdout.write(self.style.ERROR(
                            f"  ⚠️  SKIPPING {dup.email} (ID: {dup.id}) - Created on {dup.date_created}, "
                            f"outside target window! This should not happen."
                        ))
                        continue
                    
                    self.stdout.write(f"  Duplicate (DELETING): {dup.email} (ID: {dup.id}, created: {dup.date_created})")

                for duplicate in duplicates:
                    # Double-check: Only delete if created in the target time window
                    if not (start_time <= duplicate.date_created <= end_time):
                        self.stdout.write(self.style.ERROR(
                            f"    ⚠️  SAFETY: Skipping deletion of {duplicate.email} - outside target window!"
                        ))
                        continue

                    fixed_count = self._transfer_data(original, duplicate)
                    total_fixed += fixed_count
                    self.stdout.write(f"    Transferred {fixed_count} related records")

                    # SAFETY: Verify one more time before deletion
                    if not (start_time <= duplicate.date_created <= end_time):
                        raise CommandError(
                            f"CRITICAL SAFETY CHECK FAILED: Attempted to delete user {duplicate.email} "
                            f"created on {duplicate.date_created}, which is outside the target window!"
                        )

                    # Delete the duplicate (only if it's from the target date)
                    duplicate_email = duplicate.email
                    duplicate_id = duplicate.id
                    duplicate.delete()
                    total_deleted += 1
                    self.stdout.write(self.style.SUCCESS(
                        f"    ✓ Deleted duplicate user {duplicate_email} (ID: {duplicate_id})"
                    ))

        self.stdout.write(self.style.SUCCESS(
            f"\n✓ Fix complete! Fixed {total_fixed} records, deleted {total_deleted} duplicate users"
        ))
        self.stdout.write(self.style.WARNING(
            "\n⚠️  NOTE: This command only transfers data and deletes duplicates."
        ))
        self.stdout.write(self.style.WARNING(
            "⚠️  To update the original users' data (name, email, gmail, phone, etc.), "
            "you must run 'import_users_prod' again after this fix."
        ))

    def _transfer_data(self, original_user, duplicate_user):
        """Transfer all related data from duplicate to original user."""
        transferred_count = 0

        # TimelineEvent (PROTECT - need to update user FK)
        timeline_events = TimelineEvent.objects.filter(user=duplicate_user)
        count = timeline_events.update(user=original_user)
        transferred_count += count
        if count > 0:
            self.stdout.write(f"      - Transferred {count} timeline events")

        # SenioritySnapshot (CASCADE - will be deleted, need to transfer)
        seniority_snapshots = SenioritySnapshot.objects.filter(user=duplicate_user)
        count = seniority_snapshots.update(user=original_user)
        transferred_count += count
        if count > 0:
            self.stdout.write(f"      - Transferred {count} seniority snapshots")

        # CompensationSnapshot (PROTECT - need to update user FK)
        comp_snapshots = CompensationSnapshot.objects.filter(user=duplicate_user)
        count = comp_snapshots.update(user=original_user)
        transferred_count += count
        if count > 0:
            self.stdout.write(f"      - Transferred {count} compensation snapshots")

        # OrgAssignmentSnapshot (CASCADE - will be deleted, need to transfer)
        org_snapshots = OrgAssignmentSnapshot.objects.filter(user=duplicate_user)
        count = org_snapshots.update(user=original_user)
        transferred_count += count
        if count > 0:
            self.stdout.write(f"      - Transferred {count} org assignment snapshots")

        # Update leader references in org snapshots
        leader_snapshots = OrgAssignmentSnapshot.objects.filter(leader=duplicate_user)
        count = leader_snapshots.update(leader=original_user)
        transferred_count += count
        if count > 0:
            self.stdout.write(f"      - Updated {count} org snapshots with leader reference")

        # DataAccessOverride
        data_overrides = DataAccessOverride.objects.filter(user=duplicate_user)
        count = data_overrides.update(user=original_user)
        transferred_count += count
        if count > 0:
            self.stdout.write(f"      - Transferred {count} data access overrides")

        # Update granted_by references in DataAccessOverride
        granted_overrides = DataAccessOverride.objects.filter(granted_by=duplicate_user)
        count = granted_overrides.update(granted_by=original_user)
        transferred_count += count
        if count > 0:
            self.stdout.write(f"      - Updated {count} data access overrides with granted_by reference")

        # Notes
        notes = Note.objects.filter(owner=duplicate_user)
        count = notes.update(owner=original_user)
        transferred_count += count
        if count > 0:
            self.stdout.write(f"      - Transferred {count} notes")

        # Summaries
        summaries = Summary.objects.filter(note__owner=duplicate_user)
        # Summaries are linked via Note, so we need to update the note owner (already done above)
        # But we should also check for any direct references
        # Actually, Summary doesn't have a direct user FK, it's via Note

        # Feedback
        sent_feedbacks = Feedback.objects.filter(sender=duplicate_user)
        count = sent_feedbacks.update(sender=original_user)
        transferred_count += count
        if count > 0:
            self.stdout.write(f"      - Transferred {count} sent feedbacks")

        received_feedbacks = Feedback.objects.filter(receiver=duplicate_user)
        count = received_feedbacks.update(receiver=original_user)
        transferred_count += count
        if count > 0:
            self.stdout.write(f"      - Transferred {count} received feedbacks")

        # OneOnOneActivityLog
        activities = OneOnOneActivityLog.objects.filter(user=duplicate_user)
        count = activities.update(user=original_user)
        transferred_count += count
        if count > 0:
            self.stdout.write(f"      - Transferred {count} activity logs")

        # Forms
        forms = Form.objects.filter(user=duplicate_user)
        count = forms.update(user=original_user)
        transferred_count += count
        if count > 0:
            self.stdout.write(f"      - Transferred {count} forms")

        # FormAssignments
        assigned_forms = FormAssignment.objects.filter(assigned_to=duplicate_user)
        count = assigned_forms.update(assigned_to=original_user)
        transferred_count += count
        if count > 0:
            self.stdout.write(f"      - Transferred {count} form assignments (assigned_to)")

        created_assignments = FormAssignment.objects.filter(assigned_by=duplicate_user)
        count = created_assignments.update(assigned_by=original_user)
        transferred_count += count
        if count > 0:
            self.stdout.write(f"      - Transferred {count} form assignments (assigned_by)")

        # Notice, StockGrant, TitleChange (created_by references)
        notices = Notice.objects.filter(created_by=duplicate_user)
        count = notices.update(created_by=original_user)
        transferred_count += count
        if count > 0:
            self.stdout.write(f"      - Updated {count} notices (created_by)")

        stock_grants = StockGrant.objects.filter(created_by=duplicate_user)
        count = stock_grants.update(created_by=original_user)
        transferred_count += count
        if count > 0:
            self.stdout.write(f"      - Updated {count} stock grants (created_by)")

        title_changes = TitleChange.objects.filter(created_by=duplicate_user)
        count = title_changes.update(created_by=original_user)
        transferred_count += count
        if count > 0:
            self.stdout.write(f"      - Updated {count} title changes (created_by)")

        # TimelineEvent created_by references
        created_events = TimelineEvent.objects.filter(created_by=duplicate_user)
        count = created_events.update(created_by=original_user)
        transferred_count += count
        if count > 0:
            self.stdout.write(f"      - Updated {count} timeline events (created_by)")

        # User relationships (leader, agile_coach)
        # Update users who have duplicate as leader
        users_with_leader = User.objects.filter(leader=duplicate_user)
        count = users_with_leader.update(leader=original_user)
        transferred_count += count
        if count > 0:
            self.stdout.write(f"      - Updated {count} users with leader reference")

        # Update users who have duplicate as agile_coach
        users_with_coach = User.objects.filter(agile_coach=duplicate_user)
        count = users_with_coach.update(agile_coach=original_user)
        transferred_count += count
        if count > 0:
            self.stdout.write(f"      - Updated {count} users with agile_coach reference")

        # If duplicate was a leader/coach, we should preserve that relationship on original
        # But this is tricky - we might want to merge organizational data
        # For now, we'll just update the references

        return transferred_count

