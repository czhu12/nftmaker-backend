# Generated by Django 3.2.8 on 2021-11-01 19:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0003_auto_20211101_1957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='community',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contract', to='community.community'),
        ),
    ]