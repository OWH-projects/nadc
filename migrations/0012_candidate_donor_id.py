# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0011_auto_20151020_1939'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='donor_id',
            field=models.ForeignKey(to='nadc.Giver', null=True),
        ),
    ]
