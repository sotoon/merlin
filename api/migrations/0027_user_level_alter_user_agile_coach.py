# Generated by Django 5.0.1 on 2024-04-09 14:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0026_user_agile_coach"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="level",
            field=models.CharField(
                blank=True, default="", max_length=256, null=True, verbose_name="سطح"
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="agile_coach",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="coachees",
                to=settings.AUTH_USER_MODEL,
                verbose_name="PR/اجایل کوچ",
            ),
        ),
    ]
