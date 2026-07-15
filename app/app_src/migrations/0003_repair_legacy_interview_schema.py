from django.db import migrations


def repair_legacy_interview_schema(apps, schema_editor):
    connection = schema_editor.connection
    application_pack = apps.get_model("app_src", "ApplicationPack")
    interview_result = apps.get_model("app_src", "InterviewResult")

    with connection.cursor() as cursor:
        tables = set(connection.introspection.table_names(cursor))

    if application_pack._meta.db_table not in tables:
        schema_editor.create_model(application_pack)

    with connection.cursor() as cursor:
        columns = {
            column.name
            for column in connection.introspection.get_table_description(
                cursor,
                interview_result._meta.db_table,
            )
        }

    application_pack_field = interview_result._meta.get_field("application_pack")
    if application_pack_field.column not in columns:
        schema_editor.add_field(interview_result, application_pack_field)


class Migration(migrations.Migration):
    dependencies = [
        ("app_src", "0002_pack_group_system"),
    ]

    operations = [
        migrations.RunPython(
            repair_legacy_interview_schema,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
