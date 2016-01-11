# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0008_auto_20160107_2203'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ballot',
            name='nadcid',
        ),
        migrations.DeleteModel(
            name='Ballot',
        ),
    ]
