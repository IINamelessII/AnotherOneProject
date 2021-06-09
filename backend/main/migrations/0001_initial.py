# Generated by Django 2.2.6 on 2019-10-13 19:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Stats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_downloads', models.BigIntegerField(default=0)),
                ('file_uploads', models.BigIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('ext', models.CharField(max_length=10)),
                ('file', models.FileField(upload_to='')),
                ('downloads', models.IntegerField(default=0)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('mmtype', models.CharField(default='content/file', max_length=100)),
                ('owner', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='files', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Dir',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('downloads', models.IntegerField(default=0)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('dirs', models.ManyToManyField(blank=True, to='main.Dir')),
                ('files', models.ManyToManyField(blank=True, to='main.File')),
                ('owner', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='dirs', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]