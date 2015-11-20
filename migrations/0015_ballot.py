# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0014_entity'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ballot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ballot', models.CharField(max_length=80)),
                ('ballot_type', models.CharField(max_length=80)),
                ('stance', models.CharField(max_length=10, null=True, blank=True)),
                ('nadcid', models.ForeignKey(to='nadc.Getter')),
            ],
        ),
    ]
