# Generated by Django 3.2.8 on 2021-11-13 20:56

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0012_auto_20211110_2352'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pixel',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('color', models.IntegerField()),
                ('x', models.IntegerField()),
                ('y', models.IntegerField()),
                ('token_identifier', models.CharField(max_length=256)),
                ('communal_canvas', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pixels', to='community.communalcanvas')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
