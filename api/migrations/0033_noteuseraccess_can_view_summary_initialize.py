from django.db import migrations

from api.models import NoteUserAccess

def initialize_can_view_summary_access(apps, schema_editor):
    for obj in NoteUserAccess.objects.all():
        obj.ensure_note_predefined_accesses(obj.note)


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0032_noteuseraccess_can_view_summary"),
    ]

    operations = [
        migrations.RunPython(
            initialize_can_view_summary_access, migrations.RunPython.noop
        )
    ]
