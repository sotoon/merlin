# Generated by Django 5.0.1 on 2025-01-25 19:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0040_formassignment_deadline"),
    ]

    operations = [
        migrations.AddField(
            model_name="form",
            name="cycle",
            field=models.ForeignKey(
                default="2",
                on_delete=django.db.models.deletion.PROTECT,
                to="api.cycle",
                verbose_name="دوره",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="cycle",
            name="name",
            field=models.CharField(max_length=150, verbose_name="نام دوره"),
        ),
    ]
