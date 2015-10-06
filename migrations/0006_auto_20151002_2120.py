# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0005_auto_20151001_2157'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='getter',
            name='canonical',
        ),
        migrations.RemoveField(
            model_name='getter',
            name='standard_name',
        ),
    ]
