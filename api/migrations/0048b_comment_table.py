from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ("api", "0048_rename_feedback_to_comment"),
    ]

    operations = [
        migrations.AlterModelTable(
            name="comment",
            table="api_comment",
        ),
    ] 