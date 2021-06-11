# Generated by Django 3.2.4 on 2021-06-11 04:48

from django.db import migrations, models
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20210210_0111'),
    ]

    operations = [
        migrations.AlterField(
            model_name='findphoto',
            name='find_number',
            field=models.IntegerField(verbose_name='Find Number'),
        ),
        migrations.AlterField(
            model_name='findphoto',
            name='photo',
            field=models.FileField(upload_to=main.models.get_context_folder),
        ),
    ]
