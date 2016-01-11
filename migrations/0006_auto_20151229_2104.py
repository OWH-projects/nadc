# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0005_auto_20151203_1735'),
    ]

    operations = [
        migrations.AlterField(
            model_name='additionalinfo',
            name='candidate',
            field=models.CharField(help_text=b'Candidate_id from candidate table', max_length=20, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='additionalinfo',
            name='canonical',
            field=models.CharField(help_text=b'The canonical_id in the Entity table', max_length=20, null=True, blank=True),
        ),
    ]
