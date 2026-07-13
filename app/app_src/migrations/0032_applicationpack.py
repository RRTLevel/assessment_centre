import django.db.models.deletion
from django.db import migrations, models


def create_application_packs(apps, schema_editor):
    Application = apps.get_model('app_src', 'Application')
    ApplicationPack = apps.get_model('app_src', 'ApplicationPack')
    for app in Application.objects.filter(pack__isnull=False):
        ApplicationPack.objects.get_or_create(
            application=app,
            pack=app.pack,
            defaults={'order': 0},
        )


def link_interview_results(apps, schema_editor):
    InterviewResult = apps.get_model('app_src', 'InterviewResult')
    ApplicationPack = apps.get_model('app_src', 'ApplicationPack')
    for result in InterviewResult.objects.all():
        ap = ApplicationPack.objects.filter(application=result.application).order_by('order').first()
        if ap:
            result.application_pack = ap
            result.save(update_fields=['application_pack'])


class Migration(migrations.Migration):

    dependencies = [
        ('app_src', '0031_alter_interviewresponse_unique_together_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicationPack',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=0)),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interview_packs', to='app_src.application')),
                ('pack', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_src.pack')),
            ],
            options={
                'ordering': ['order'],
                'unique_together': {('application', 'pack')},
            },
        ),
        migrations.RunPython(create_application_packs, reverse_code=migrations.RunPython.noop),
        migrations.AddField(
            model_name='interviewresult',
            name='application_pack',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='results',
                to='app_src.applicationpack',
            ),
        ),
        migrations.RunPython(link_interview_results, reverse_code=migrations.RunPython.noop),
    ]
