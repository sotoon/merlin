# Generated by Django 5.0.1 on 2024-02-11 21:46

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0011_tribe_team_tribe"),
    ]

    operations = [
        migrations.AlterField(
            model_name="note",
            name="type",
            field=models.CharField(
                choices=[
                    ("Goal", "هدف"),
                    ("Meeting", "جلسه"),
                    ("Personal", "شخصی"),
                    ("Task", "فعالیت"),
                    ("Propsal", "پروپوزال"),
                ],
                default="Goal",
                max_length=128,
                verbose_name="نوع",
            ),
        ),
        migrations.CreateModel(
            name="Committee",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                (
                    "date_created",
                    models.DateTimeField(
                        auto_now_add=True, null=True, verbose_name="تاریخ ساخت"
                    ),
                ),
                (
                    "date_updated",
                    models.DateTimeField(
                        auto_now=True, null=True, verbose_name="تاریخ بروزرسانی"
                    ),
                ),
                ("name", models.CharField(max_length=256, verbose_name="نام")),
                ("description", models.TextField(blank=True, verbose_name="توضیحات")),
                (
                    "members",
                    models.ManyToManyField(
                        to=settings.AUTH_USER_MODEL, verbose_name="اعضا"
                    ),
                ),
            ],
            options={
                "verbose_name": "کمیته",
                "verbose_name_plural": "کمیته\u200cها",
            },
        ),
        migrations.AddField(
            model_name="note",
            name="committee",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="api.committee",
            ),
        ),
    ]
