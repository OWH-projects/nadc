# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='donation',
            old_name='inkinddesc',
            new_name='inkind_desc',
        ),
        migrations.RenameField(
            model_name='getter',
            old_name='standardname',
            new_name='standard_name',
        ),
        migrations.RenameField(
            model_name='giver',
            old_name='standdardname',
            new_name='standard_name',
        ),
    ]
