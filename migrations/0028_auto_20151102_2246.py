# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0027_auto_20151102_2208'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='donor_name',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='expenditure',
            name='committee_exp_name',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
    ]
