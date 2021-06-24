# Generated by Django 3.2.4 on 2021-06-24 07:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0009_averagewalked'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='binarywalked',
            index=models.Index(fields=['local_datetime', 'user_id'], name='data_binary_local_d_172f83_idx'),
        ),
        migrations.AddIndex(
            model_name='binarywalked',
            index=models.Index(fields=['user_id'], name='data_binary_user_id_ac75a1_idx'),
        ),
    ]