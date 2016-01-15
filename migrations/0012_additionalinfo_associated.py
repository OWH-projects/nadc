# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0011_auto_20160111_1829'),
    ]

    operations = [
        migrations.AddField(
            model_name='additionalinfo',
            name='associated',
            field=models.ManyToManyField(help_text=b'Associated groups we want to tie to this person. For example, a business or PAC', to='nadc.Entity', null=True, blank=True),
        ),
    ]
