from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_src', '0027_remove_indicator_category'),
    ]

    operations = [
        # 1. Drop old unique constraint (references 'result' column)
        migrations.AlterUniqueTogether(
            name='indicatorscore',
            unique_together=set(),
        ),
        # 2. Clear all existing rows — old per-question scores are incompatible
        #    with the new per-application model, and keeping them causes duplicate
        #    (application_id, indicator_id) pairs after the backfill.
        migrations.RunSQL(
            sql="DELETE FROM app_src_indicatorscore;",
            reverse_sql="",
        ),
        # 3. Add application FK (nullable while result column still exists)
        migrations.AddField(
            model_name='indicatorscore',
            name='application',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='indicator_scores',
                to='app_src.application',
            ),
        ),
        # 4. Drop the old result FK
        migrations.RemoveField(
            model_name='indicatorscore',
            name='result',
        ),
        # 5. Make application non-nullable (safe — no rows exist)
        migrations.AlterField(
            model_name='indicatorscore',
            name='application',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='indicator_scores',
                to='app_src.application',
            ),
        ),
        # 6. Add new unique constraint
        migrations.AlterUniqueTogether(
            name='indicatorscore',
            unique_together={('application', 'indicator')},
        ),
    ]
