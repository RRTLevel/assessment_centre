from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_src', '0026_indicator_category_alter_indicator_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='indicator',
            name='category',
        ),
    ]
