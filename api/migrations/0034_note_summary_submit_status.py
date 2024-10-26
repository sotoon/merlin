# Generated by Django 5.0.1 on 2024-10-26 10:03

from django.db import migrations, models
from api.models import SubmitStatus

def set_initial_submit_status_for_existing_notes_summaries(apps, schema_editor):
    Note = apps.get_model('api', 'Note')
    Summary = apps.get_model('api', 'Summary')

    Note.objects.filter(submit_status=SubmitStatus.DRAFT).update(submit_status=SubmitStatus.INITIAL_SUBMIT)
    Summary.objects.filter(submit_status=SubmitStatus.DRAFT).update(submit_status=SubmitStatus.INITIAL_SUBMIT)


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0033_noteuseraccess_can_view_summary_initialize'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='submit_status',
            field=models.IntegerField(choices=[(0, 'درفت'), (1, 'ثبت اولیه'), (2, 'ثبت نهایی')], default=0, verbose_name='وضعیت'),
        ),
        migrations.AddField(
            model_name='summary',
            name='submit_status',
            field=models.IntegerField(choices=[(0, 'درفت'), (1, 'ثبت اولیه'), (2, 'ثبت نهایی')], default=0, verbose_name='وضعیت'),
        ),
        migrations.RunPython(set_initial_submit_status_for_existing_notes_summaries),
    ]
