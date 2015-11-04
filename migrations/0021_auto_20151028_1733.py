# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0020_auto_20151027_1456'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Giver',
        ),
        migrations.AddField(
            model_name='donation',
            name='stance',
            field=models.CharField(max_length=10, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='loan',
            name='stance',
            field=models.CharField(max_length=10, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='ballot',
            name='nadcid',
            field=models.ForeignKey(to='nadc.Entity'),
        ),
        migrations.DeleteModel(
            name='Getter',
        ),
    ]
