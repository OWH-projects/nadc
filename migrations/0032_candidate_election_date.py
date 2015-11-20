# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0031_auto_20151105_2208'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='election_date',
            field=models.DateField(null=True, blank=True),
        ),
    ]
