from django.core.management.base import BaseCommand
from django.db.models.signals import post_save
from django.conf import settings

from api.models import Note
from api.models import Note, NoteUserAccess, User


User = settings.AUTH_USER_MODEL


class Command(BaseCommand):
    help = "Updates permissions for new leader"

    def add_arguments(self, parser):
        parser.add_argument('--former_email', type=str, help='former leader email')
        parser.add_argument('--new_email', type=str, help='new leader email')


    def handle(self, *args, **options):
        if options['former_email'] is None:
            print("--former_email should not be empty")
            return
        if options["new_email"] is None:
            print("--new_email should not be empty")
            return
        former_email = options["former_email"]
        new_email = options["new_email"]
        former_leader = User.objects.get(email=former_email)
        new_leader = User.objects.get(email=new_email)
        User.objects.filter(leader=former_leader).update(leader=new_leader)
        NoteUserAccess.objects.filter(user=former_leader) \
            .exclude(note__owner=former_leader) \
                .update(
                    defaults={
                        "can_view": False,
                        "can_edit": False,
                        "can_view_summary": False,
                        "can_write_summary": False,
                        "can_write_feedback": False,
                        "can_view_feedbacks": False,
                        },
                    )

        for note in Note.objects.all():
            post_save.send(sender=Note, instance=note, created=False)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully updated access permissions for note {note.id}"
                )
            )
