from django.db import migrations


ACCOUNT_TYPE_GROUPS = [
    "Admin",
    "Assessor",
    "Early Careers Definer",
    "Early Careers Assessment Manager",
]


def create_account_type_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")

    for name in ACCOUNT_TYPE_GROUPS:
        Group.objects.get_or_create(name=name)


def delete_account_type_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=ACCOUNT_TYPE_GROUPS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("app_src", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(
            create_account_type_groups,
            delete_account_type_groups,
        ),
    ]
