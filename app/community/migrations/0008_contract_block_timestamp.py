# Generated by Django 3.2.8 on 2021-11-02 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0007_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='block_timestamp',
            field=models.BigIntegerField(default=0),
        ),
    ]