# Generated by Django 3.2.4 on 2021-06-28 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0014_predicted_actual'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='threehour',
            index=models.Index(fields=['user_id', 'local_date', 'step', 'window_size', 'threshold1'], name='data_threeh_user_id_d87968_idx'),
        ),
    ]
