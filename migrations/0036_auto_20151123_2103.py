# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0035_auto_20151123_2005'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='candidate',
            name='election_date',
        ),
        migrations.AddField(
            model_name='entity',
            name='registered_date',
            field=models.DateField(null=True, blank=True),
        ),
    ]
