# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0033_auto_20151120_1518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expenditure',
            name='target_candidate',
            field=models.ForeignKey(related_name='committee_target_candidate', blank=True, to='nadc.Candidate', null=True),
        ),
    ]
