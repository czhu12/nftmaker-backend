# Generated by Django 3.2.8 on 2021-10-21 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('editor', '0003_auto_20211020_0532'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='height',
            field=models.IntegerField(default=512),
        ),
        migrations.AddField(
            model_name='project',
            name='width',
            field=models.IntegerField(default=512),
        ),
    ]
