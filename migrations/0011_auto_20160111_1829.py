# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0010_donation_source_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donation',
            name='id',
            field=models.IntegerField(serialize=False, primary_key=True),
        ),
    ]
