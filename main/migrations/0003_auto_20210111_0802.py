# Generated by Django 3.1.3 on 2021-01-11 08:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import main.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0002_auto_20210104_1603'),
    ]

    operations = [
        migrations.AddField(
            model_name='contextphoto',
            name='created',
            field=models.DateTimeField(default=main.models.utc_now, verbose_name='Created'),
        ),
        migrations.AlterField(
            model_name='contextphoto',
            name='context_number',
            field=models.IntegerField(verbose_name='Context Number'),
        ),
        migrations.CreateModel(
            name='ActionLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('model_name', models.CharField(max_length=100, verbose_name='Model Name')),
                ('timestamp', models.DateTimeField(default=main.models.utc_now, verbose_name='timestamp')),
                ('action', models.CharField(choices=[('C', 'CREATE'), ('R', 'READ'), ('U', 'UPDATE'), ('D', 'DELETE')], max_length=2, verbose_name='Action Type')),
                ('object_id', models.UUIDField(verbose_name='Object ID')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Action Log',
                'verbose_name_plural': 'Action Logs',
                'db_table': 'action_log',
            },
        ),
    ]
