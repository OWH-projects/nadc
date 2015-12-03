# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='govslug',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
