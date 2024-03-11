from django.core.management.base import BaseCommand
from django.db.models.signals import post_save

from api.models import Note


class Command(BaseCommand):
    help = "Updates access permissions for all notes"

    def handle(self, *args, **options):
        for note in Note.objects.all():
            post_save.send(sender=Note, instance=note, created=False)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully updated access permissions for note {note.id}"
                )
            )
