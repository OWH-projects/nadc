# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0029_entity_dissolved_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expenditure',
            name='committee',
            field=models.ForeignKey(related_name='committee_exp', blank=True, to='nadc.Entity', null=True),
        ),
        migrations.AlterField(
            model_name='loan',
            name='committee',
            field=models.ForeignKey(related_name='committee_lendee', blank=True, to='nadc.Entity', null=True),
        ),
    ]
