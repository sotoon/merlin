# Generated by Django 5.0.1 on 2024-02-25 20:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0017_alter_note_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="note",
            name="is_public",
            field=models.BooleanField(default=False, verbose_name="عمومی"),
        ),
    ]