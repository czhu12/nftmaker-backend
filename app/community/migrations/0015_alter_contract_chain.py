# Generated by Django 3.2.8 on 2021-11-18 00:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0014_contract_chain'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='chain',
            field=models.CharField(choices=[('eth', 'eth'), ('polygon', 'polygon')], default='eth', max_length=64),
        ),
    ]
