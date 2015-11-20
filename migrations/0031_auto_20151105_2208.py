# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0030_auto_20151105_2046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='cand_name',
            field=models.CharField(max_length=70, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='donation',
            name='recipient',
            field=models.ForeignKey(related_name='getter', blank=True, to='nadc.Entity', null=True),
        ),
        migrations.AlterField(
            model_name='expenditure',
            name='payee',
            field=models.CharField(max_length=70, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='loan',
            name='guarantor',
            field=models.CharField(max_length=70, null=True, blank=True),
        ),
    ]
