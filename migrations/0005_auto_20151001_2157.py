# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0004_auto_20151001_2114'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='donation',
            name='source',
        ),
        migrations.AddField(
            model_name='donation',
            name='donation_year',
            field=models.CharField(default=b'', max_length=4),
        ),
    ]
