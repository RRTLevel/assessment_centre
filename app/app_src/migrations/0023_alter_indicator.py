from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_src', '0022_merge_20260629_0931'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='indicator',
            name='text',
        ),
        migrations.RemoveField(
            model_name='indicator',
            name='category',
        ),
        migrations.AddField(
            model_name='indicator',
            name='positive',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='indicator',
            name='negative',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='indicator',
            name='question',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='indicators',
                to='app_src.questions',
            ),
        ),
    ]
