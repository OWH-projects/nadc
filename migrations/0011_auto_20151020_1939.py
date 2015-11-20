# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0010_auto_20151020_1826'),
    ]

    operations = [
        migrations.AddField(
            model_name='expenditure',
            name='issue',
            field=models.CharField(max_length=75, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='expenditure',
            name='stance',
            field=models.CharField(max_length=10, null=True, blank=True),
        ),
    ]
