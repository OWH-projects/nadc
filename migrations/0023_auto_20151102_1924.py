# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0022_garbagefire'),
    ]

    operations = [
        migrations.AddField(
            model_name='loan',
            name='lending_committee',
            field=models.ForeignKey(related_name='committee_lender', blank=True, to='nadc.Entity', null=True),
        ),
        migrations.AlterField(
            model_name='loan',
            name='committee',
            field=models.ForeignKey(related_name='committee_lendee', to='nadc.Entity'),
        ),
    ]
