# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0026_auto_20151102_2100'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='garbagefire',
            name='nadcid',
        ),
        migrations.AlterField(
            model_name='donation',
            name='donor',
            field=models.ForeignKey(related_name='giver', blank=True, to='nadc.Entity', null=True),
        ),
        migrations.DeleteModel(
            name='GarbageFire',
        ),
    ]
