# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0009_expenditure'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='office_desc',
            field=models.CharField(max_length=30, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='candidate',
            name='office_sought',
            field=models.CharField(max_length=30, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='candidate',
            name='office_title',
            field=models.CharField(max_length=30, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='candidate',
            name='stance',
            field=models.CharField(max_length=2, null=True, blank=True),
        ),
    ]
