# Generated by Django 5.0.1 on 2025-07-13 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0049_feedbackform_alter_note_type_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="oneonone",
            name="career_summary",
            field=models.CharField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="oneonone",
            name="communication_summary",
            field=models.CharField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="oneonone",
            name="performance_summary",
            field=models.CharField(max_length=800),
        ),
        migrations.AlterField(
            model_name="oneonone",
            name="personal_summary",
            field=models.CharField(blank=True, null=True),
        ),
    ]
