# Generated by Django 3.1.3 on 2021-01-22 23:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_bagphoto'),
    ]

    operations = [
        migrations.AddField(
            model_name='bagphoto',
            name='source',
            field=models.CharField(choices=[('F', 'In Field'), ('D', 'Drying')], default='F', max_length=1, verbose_name='Location where taken'),
        ),
    ]
