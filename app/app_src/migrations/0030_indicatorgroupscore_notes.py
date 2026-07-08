from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_src', '0029_indicatorgroupscore'),
    ]

    operations = [
        migrations.AddField(
            model_name='indicatorgroupscore',
            name='notes',
            field=models.TextField(blank=True, default=''),
        ),
    ]
