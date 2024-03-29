# Generated by Django 5.0.1 on 2024-03-11 08:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0023_alter_noteuseraccess_can_view_feedbacks"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="note",
            name="committee",
        ),
        migrations.AddField(
            model_name="user",
            name="committee",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="committee_users",
                to="api.committee",
                verbose_name="کمیته",
            ),
        ),
        migrations.AlterField(
            model_name="committee",
            name="members",
            field=models.ManyToManyField(
                related_name="committee_members",
                to=settings.AUTH_USER_MODEL,
                verbose_name="اعضا",
            ),
        ),
    ]
