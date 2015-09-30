# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='donation',
            name='donor',
        ),
        migrations.RemoveField(
            model_name='donation',
            name='recipient',
        ),
        migrations.DeleteModel(
            name='Donation',
        ),
        migrations.DeleteModel(
            name='Getter',
        ),
        migrations.DeleteModel(
            name='Giver',
        ),
    ]
