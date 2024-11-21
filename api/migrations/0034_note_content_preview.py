import re
from django.db import migrations, models


def initialize_note_content(apps, schema_editor):
    Note = apps.get_model("api", "Note")

    for instance in Note.objects.all():
        if instance.content:
            instance.content_preview = re.sub("<.*?>", " ", instance.content)[:200]
            instance.save()


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0033_noteuseraccess_can_view_summary_initialize"),
    ]

    operations = [
        migrations.AddField(
            model_name="note",
            name="content_preview",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.RunPython(initialize_note_content, migrations.RunPython.noop),
    ]
