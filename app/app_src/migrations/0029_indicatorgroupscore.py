from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_src', '0028_alter_indicatorscore'),
    ]

    operations = [
        migrations.CreateModel(
            name='IndicatorGroupScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_name', models.CharField(max_length=100)),
                ('score', models.IntegerField()),
                ('application', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='indicator_group_scores',
                    to='app_src.application',
                )),
            ],
            options={
                'unique_together': {('application', 'group_name')},
            },
        ),
    ]
