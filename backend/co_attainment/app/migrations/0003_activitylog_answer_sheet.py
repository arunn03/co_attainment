# Generated by Django 4.2.16 on 2024-10-14 16:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_remove_staff_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='activitylog',
            name='answer_sheet',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='app.answersheet'),
        ),
    ]