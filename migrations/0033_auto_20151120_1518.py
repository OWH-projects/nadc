# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0032_candidate_election_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='expenditure',
            name='raw_target',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='expenditure',
            name='target_candidate',
            field=models.ForeignKey(related_name='committee_target_candidate', blank=True, to='nadc.Entity', null=True),
        ),
        migrations.AddField(
            model_name='expenditure',
            name='target_committee',
            field=models.ForeignKey(related_name='committee_target_committee', blank=True, to='nadc.Entity', null=True),
        ),
    ]
