from django.db import migrations

PREDEFINED_ROLES = [
    # {"role_type": "Leader", "role_scope": "User"},
    # {"role_type": "PRODUCT_MANAGER", "role_scope": "User"},
    # {"role_type": "Leader", "role_scope": "Chapter"},
    # {"role_type": "Director", "role_scope": "TRIBE"},
    {"role_type": "CTO", "role_scope": "Organization"},
    {"role_type": "VP", "role_scope": "Organization"},
    {"role_type": "CEO", "role_scope": "Organization"},
    {"role_type": "Function_Owner", "role_scope": "Organization"},
]

def populate_roles(apps, schema_editor):
    GeneralRole = apps.get_model('api', 'GeneralRole')
    for role_data in PREDEFINED_ROLES:
        GeneralRole.objects.get_or_create(**role_data)

def reverse_populate_roles(apps, schema_editor):
    GeneralRole = apps.get_model('api', 'GeneralRole')
    for role_data in PREDEFINED_ROLES:
        GeneralRole.objects.filter(**role_data).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0044_add_role_committee'),
    ]

    operations = [
        migrations.RunPython(populate_roles, reverse_code=reverse_populate_roles),
    ]
