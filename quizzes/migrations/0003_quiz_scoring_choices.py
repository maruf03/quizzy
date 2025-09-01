from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("quizzes", "0002_invitation_declined"),
    ]

    operations = [
        migrations.AlterField(
            model_name="quiz",
            name="scoring_policy",
            field=models.CharField(choices=[('best','Best'),('first','First'),('last','Last')], max_length=10, default='best'),
        ),
    ]
