# Generated by Django 3.2.8 on 2021-10-29 04:50

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NftReveal',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('slug', models.CharField(max_length=256, unique=True)),
                ('contract_address', models.CharField(max_length=256)),
                ('latest_token_id', models.IntegerField(default=None, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
