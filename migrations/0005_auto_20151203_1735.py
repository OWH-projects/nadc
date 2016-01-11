# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0004_auto_20151202_2200'),
    ]

    operations = [
        migrations.AddField(
            model_name='additionalinfo',
            name='care',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='additionalinfo',
            name='name',
            field=models.CharField(default='Pete Ricketts', max_length=120),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='additionalinfo',
            name='mugshot',
            field=models.FileField(null=True, upload_to=b'nadc/mugs/', blank=True),
        ),
        migrations.AlterField(
            model_name='additionalinfo',
            name='title',
            field=models.CharField(max_length=120, null=True, blank=True),
        ),
    ]
