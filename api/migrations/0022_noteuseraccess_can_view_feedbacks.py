# Generated by Django 5.0.1 on 2024-03-11 05:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0021_noteuseraccess_can_write_feedback"),
    ]

    operations = [
        migrations.AddField(
            model_name="noteuseraccess",
            name="can_view_feedbacks",
            field=models.BooleanField(default=False, verbose_name="مشاهده فیدبک"),
        ),
    ]
