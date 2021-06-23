# Generated by Django 3.2.4 on 2021-06-23 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0006_delete_padded_steps'),
    ]

    operations = [
        migrations.CreateModel(
            name='Padded_Steps',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('local_datetime', models.DateTimeField()),
                ('user_id', models.IntegerField()),
                ('steps', models.IntegerField()),
                ('local_date', models.DateField(blank=True, null=True)),
                ('local_time', models.TimeField(blank=True, null=True)),
            ],
        ),
    ]
