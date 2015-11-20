# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0015_ballot'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ballot',
            name='ballot_type',
            field=models.CharField(max_length=5),
        ),
    ]
