# Generated by Django 4.2.16 on 2024-10-16 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_alter_answersheet_marks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answersheet',
            name='marks',
            field=models.JSONField(),
        ),
    ]