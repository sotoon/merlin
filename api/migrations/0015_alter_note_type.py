# Generated by Django 5.0.1 on 2024-02-18 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0014_alter_note_type"),
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
                    ("Proposal", "پروپوزال"),
                    ("Message", "پیام"),
                ],
                default="Goal",
                max_length=128,
                verbose_name="نوع",
            ),
        ),
    ]