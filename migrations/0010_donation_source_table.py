# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0009_auto_20160107_2305'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='source_table',
            field=models.CharField(max_length=10, null=True, blank=True),
        ),
    ]
