# Generated by Django 3.2.4 on 2021-06-23 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0003_task'),
    ]

    operations = [
        migrations.AddField(
            model_name='rawsteps',
            name='local_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rawsteps',
            name='local_time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
