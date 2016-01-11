# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0007_auto_20160107_1558'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donation',
            name='donation_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='expenditure',
            name='exp_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='loan',
            name='loan_date',
            field=models.DateField(null=True, blank=True),
        ),
    ]
