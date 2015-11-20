# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0006_auto_20151002_2120'),
    ]

    operations = [
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cand_id', models.CharField(max_length=40)),
                ('cand_name', models.CharField(max_length=70)),
                ('committee', models.ForeignKey(to='nadc.Getter')),
            ],
        ),
    ]
