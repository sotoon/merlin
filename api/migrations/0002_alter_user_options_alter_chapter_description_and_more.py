# Generated by Django 5.0.1 on 2024-01-24 23:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="user",
            options={"verbose_name": "کاربر", "verbose_name_plural": "کاربران"},
        ),
        migrations.AlterField(
            model_name="chapter",
            name="description",
            field=models.TextField(default="", verbose_name="توضیحات"),
        ),
        migrations.AlterField(
            model_name="department",
            name="description",
            field=models.TextField(default="", verbose_name="توضیحات"),
        ),
        migrations.AlterField(
            model_name="team",
            name="description",
            field=models.TextField(default="", verbose_name="توضیحات"),
        ),
    ]
