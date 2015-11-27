# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0036_auto_20151123_2103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='office_dist',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='office_govt',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='office_title',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
