# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0016_auto_20151022_1718'),
    ]

    operations = [
        migrations.AddField(
            model_name='ballot',
            name='notes',
            field=models.TextField(null=True, blank=True),
        ),
    ]
