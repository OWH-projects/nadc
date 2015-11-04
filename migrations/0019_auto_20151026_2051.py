# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0018_auto_20151026_1453'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='committee',
            field=models.ForeignKey(related_name='candidate_detail', to='nadc.Entity'),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='donor_id',
            field=models.ForeignKey(to='nadc.Entity', null=True),
        ),
        migrations.AlterField(
            model_name='expenditure',
            name='issue',
            field=models.ForeignKey(related_name='indexp', to='nadc.Entity', null=True),
        ),
    ]
