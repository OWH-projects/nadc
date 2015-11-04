# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0028_auto_20151102_2246'),
    ]

    operations = [
        migrations.AddField(
            model_name='entity',
            name='dissolved_date',
            field=models.DateField(null=True, blank=True),
        ),
    ]
