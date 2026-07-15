import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_src', '0033_genre'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='questions',
            name='genre',
        ),
        migrations.AddField(
            model_name='genre',
            name='pack_1',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='genres_as_slot_1',
                to='app_src.Pack',
            ),
        ),
        migrations.AddField(
            model_name='genre',
            name='pack_2',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='genres_as_slot_2',
                to='app_src.Pack',
            ),
        ),
        migrations.AddField(
            model_name='genre',
            name='pack_3',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='genres_as_slot_3',
                to='app_src.Pack',
            ),
        ),
    ]
