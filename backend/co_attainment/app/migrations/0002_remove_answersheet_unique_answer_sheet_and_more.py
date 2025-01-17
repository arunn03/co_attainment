# Generated by Django 4.2.16 on 2024-12-26 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='answersheet',
            name='unique_answer_sheet',
        ),
        migrations.AddConstraint(
            model_name='answersheet',
            constraint=models.UniqueConstraint(fields=('student', 'year', 'semester', 'exam_type', 'subject', 'is_deleted'), name='unique_answer_sheet'),
        ),
    ]
