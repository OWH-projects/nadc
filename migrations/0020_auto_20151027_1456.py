# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0019_auto_20151026_2051'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='donor_id',
            field=models.CharField(max_length=30, null=True, blank=True),
        ),
    ]
