# Generated by Django 3.2.18 on 2023-09-13 07:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0007_auto_20210611_0448'),
    ]

    operations = [
        migrations.CreateModel(
            name='SurveyPath',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('notes', models.TextField(blank=True, default='', verbose_name='Notes')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SurveyPoint',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('utm_hemisphere', models.CharField(choices=[('N', 'North'), ('S', 'South')], max_length=1, verbose_name='UTM Hemisphere')),
                ('utm_zone', models.IntegerField(verbose_name='UTM Zone')),
                ('utm_easting_meters', models.DecimalField(decimal_places=3, max_digits=9, verbose_name='Easting (meters)')),
                ('utm_northing_meters', models.DecimalField(decimal_places=3, max_digits=10, verbose_name='Northing (meters)')),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9, verbose_name='Latitude (decimal degrees)')),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9, verbose_name='Longitude (decimal degrees)')),
                ('utm_altitude', models.DecimalField(decimal_places=4, max_digits=8, verbose_name='Elevation (meters)')),
                ('source', models.CharField(choices=[('G', 'Phone GPS'), ('R', 'Reach')], max_length=1, verbose_name='Source')),
                ('timestamp', models.DateTimeField(verbose_name='Timestamp')),
                ('survey_path', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.surveypath')),
            ],
            options={
                'ordering': ['survey_path', 'timestamp'],
            },
        ),
    ]
