from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_src', '0023_alter_indicator'),
    ]

    operations = [
        migrations.AddField(
            model_name='indicator',
            name='name',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.CreateModel(
            name='IndicatorScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField()),
                ('indicator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_src.indicator')),
                ('result', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='indicator_scores', to='app_src.interviewresult')),
            ],
            options={
                'unique_together': {('result', 'indicator')},
            },
        ),
    ]
