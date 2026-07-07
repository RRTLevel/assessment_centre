from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_src', '0027_remove_indicator_category'),
    ]

    operations = [
        # Clear unique_together first so 'result' isn't referenced during column drop
        migrations.AlterUniqueTogether(
            name='indicatorscore',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='indicatorscore',
            name='application',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='indicator_scores',
                to='app_src.application',
                default=1,
            ),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='indicatorscore',
            name='result',
        ),
        migrations.AlterUniqueTogether(
            name='indicatorscore',
            unique_together={('application', 'indicator')},
        ),
    ]
