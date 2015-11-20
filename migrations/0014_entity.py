# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0013_auto_20151021_2046'),
    ]

    operations = [
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('nadcid', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('canonical', models.CharField(max_length=10, null=True, blank=True)),
                ('name', models.CharField(max_length=80)),
                ('standard_name', models.CharField(max_length=80)),
                ('address', models.CharField(max_length=75, null=True, blank=True)),
                ('city', models.CharField(max_length=40, null=True, blank=True)),
                ('state', models.CharField(max_length=40, null=True, blank=True)),
                ('zip', models.CharField(max_length=20, null=True, blank=True)),
                ('entity_type', models.CharField(max_length=15, null=True, blank=True)),
                ('notes', models.TextField(null=True, blank=True)),
            ],
        ),
    ]
