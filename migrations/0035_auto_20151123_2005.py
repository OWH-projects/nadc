# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0034_auto_20151123_1815'),
    ]

    operations = [
        migrations.RenameField(
            model_name='candidate',
            old_name='office_desc',
            new_name='office_dist',
        ),
        migrations.RenameField(
            model_name='candidate',
            old_name='office_sought',
            new_name='office_govt',
        ),
    ]
