# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0025_remove_expenditure_issue'),
    ]

    operations = [
        migrations.AddField(
            model_name='entity',
            name='employer',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='entity',
            name='occupation',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='entity',
            name='place_of_business',
            field=models.TextField(null=True, blank=True),
        ),
    ]
