# Generated by Django 5.0.1 on 2024-04-07 21:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0025_note_linked_notes"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="agile_coach",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="coachees",
                to=settings.AUTH_USER_MODEL,
                verbose_name="اجایل کوچ",
            ),
        ),
    ]
