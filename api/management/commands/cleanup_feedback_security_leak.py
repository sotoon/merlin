from django.core.management.base import BaseCommand
from django.db import models
from django.db.models import Q
from api.models import NoteUserAccess, Note, NoteType


class Command(BaseCommand):
    help = "Remove unauthorized access grants for existing feedback notes (security leak cleanup)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Find all feedback notes
        feedback_notes = Note.objects.filter(
            type__in=[NoteType.FEEDBACK, NoteType.FEEDBACK_REQUEST]
        )
        
        self.stdout.write(f"Found {feedback_notes.count()} feedback notes")
        
        # Find wrong access records that shouldn't exist
        # These are access records for feedback notes where the user is NOT:
        # - The note owner
        # - The feedback receiver  
        # - Mentioned in the note
        wrong_access = NoteUserAccess.objects.filter(
            note__in=feedback_notes
        ).exclude(
            # Keep legitimate access records
            Q(user=models.F('note__owner')) |  # Owner
            Q(user=models.F('note__feedback__receiver')) |  # Receiver
            Q(user__in=models.F('note__mentioned_users'))  # Mentioned users
        )
        
        count = wrong_access.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS("No unauthorized access records found. Security is clean!")
            )
            return
        
        # Show details of what will be removed
        self.stdout.write(f"\nFound {count} unauthorized access records:")
        
        for access in wrong_access.select_related('user', 'note')[:10]:  # Show first 10
            self.stdout.write(
                f"  - {access.user.name or access.user.email} → "
                f"{access.note.title} ({access.note.type})"
            )
        
        if count > 10:
            self.stdout.write(f"  ... and {count - 10} more")
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"\nDRY RUN: Would remove {count} unauthorized access records")
            )
            self.stdout.write("Run without --dry-run to actually remove them")
        else:
            # Confirm before deletion
            confirm = input(f"\nRemove {count} unauthorized access records? (yes/no): ")
            if confirm.lower() in ['yes', 'y']:
                wrong_access.delete()
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully removed {count} unauthorized access records")
                )
                self.stdout.write(
                    self.style.SUCCESS("Security leak has been patched!")
                )
            else:
                self.stdout.write("Operation cancelled")
