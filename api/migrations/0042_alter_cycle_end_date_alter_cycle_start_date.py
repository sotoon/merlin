# Generated by Django 5.0.1 on 2025-01-25 20:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0041_form_cycle_alter_cycle_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cycle",
            name="end_date",
            field=models.DateTimeField(verbose_name="تاریخ پایان"),
        ),
        migrations.AlterField(
            model_name="cycle",
            name="start_date",
            field=models.DateTimeField(verbose_name="تاریخ شروع"),
        ),
    ]
