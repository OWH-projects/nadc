# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0012_candidate_donor_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='notes',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='donation',
            name='notes',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='expenditure',
            name='notes',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='getter',
            name='notes',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='giver',
            name='notes',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='loan',
            name='notes',
            field=models.TextField(null=True, blank=True),
        ),
    ]
