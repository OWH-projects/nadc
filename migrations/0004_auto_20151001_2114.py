# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0003_auto_20150930_1931'),
    ]

    operations = [
        migrations.RenameField(
            model_name='donation',
            old_name='date',
            new_name='donation_date',
        ),
    ]
