from django.db import migrations

def seed_questions(apps, schema_editor):
    QuestionTable = apps.get_model("app_src", "QuestionTable")
    
    # Clear out the old "Random Q" data first so they don't mix
    QuestionTable.objects.all().delete()

    # Seed your clean list
    QuestionTable.objects.create(question="Category 1 - Question 1")
    QuestionTable.objects.create(question="Category 1 - Question 2")
    QuestionTable.objects.create(question="Category 1 - Question 3")
    QuestionTable.objects.create(question="Category 1 - Question 4")
    QuestionTable.objects.create(question="Category 2 - Question 1")
    QuestionTable.objects.create(question="Category 2 - Question 2")
    QuestionTable.objects.create(question="Category 2 - Question 3")
    QuestionTable.objects.create(question="Category 2 - Question 4")
    QuestionTable.objects.create(question="Category 3 - Question 1")
    QuestionTable.objects.create(question="Category 3 - Question 2")
    QuestionTable.objects.create(question="Category 3 - Question 3")
    QuestionTable.objects.create(question="Category 3 - Question 4")
    QuestionTable.objects.create(question="Category 4 - Question 1")
    QuestionTable.objects.create(question="Category 4 - Question 2")
    QuestionTable.objects.create(question="Category 4 - Question 3")
    QuestionTable.objects.create(question="Category 4 - Question 4")

class Migration(migrations.Migration):

    dependencies = [
        ('app_src', '0003_questiontable'), # Links directly to your model setup
    ]

    operations = [
        migrations.RunPython(seed_questions),
    ]