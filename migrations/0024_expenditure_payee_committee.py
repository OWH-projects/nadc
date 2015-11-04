# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0023_auto_20151102_1924'),
    ]

    operations = [
        migrations.AddField(
            model_name='expenditure',
            name='payee_committee',
            field=models.ForeignKey(related_name='committee_payee', blank=True, to='nadc.Entity', null=True),
        ),
    ]
