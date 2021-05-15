# Generated by Django 3.1.3 on 2021-02-10 01:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import main.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0005_bagphoto_source'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bagphoto',
            name='photo',
            field=models.ImageField(upload_to=main.models.get_context_folder),
        ),
        migrations.AlterField(
            model_name='bagphoto',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to=main.models.get_context_folder_tn),
        ),
        migrations.AlterField(
            model_name='contextphoto',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to=main.models.get_context_folder_tn),
        ),
        migrations.CreateModel(
            name='FindPhoto',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('utm_hemisphere', models.CharField(choices=[('N', 'North'), ('S', 'South')], max_length=1, verbose_name='UTM Hemisphere')),
                ('utm_zone', models.IntegerField(verbose_name='UTM Zone')),
                ('area_utm_easting_meters', models.IntegerField(verbose_name='Easting (meters)')),
                ('area_utm_northing_meters', models.IntegerField(verbose_name='Northing (meters)')),
                ('context_number', models.IntegerField(verbose_name='Context Number')),
                ('find_number', models.IntegerField(verbose_name='Context Number')),
                ('photo', models.ImageField(upload_to=main.models.get_context_folder)),
                ('created', models.DateTimeField(default=main.models.utc_now, verbose_name='Created')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Find Photo',
                'verbose_name_plural': 'Find Photos',
                'db_table': 'find_photos',
            },
        ),
    ]
