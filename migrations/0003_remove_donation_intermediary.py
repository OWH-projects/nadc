# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0002_auto_20150923_1713'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='donation',
            name='intermediary',
        ),
    ]
