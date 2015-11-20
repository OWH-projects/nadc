# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0017_ballot_notes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='committee',
            field=models.ForeignKey(to='nadc.Entity'),
        ),
        migrations.AlterField(
            model_name='donation',
            name='donor',
            field=models.ForeignKey(related_name='giver', to='nadc.Entity'),
        ),
        migrations.AlterField(
            model_name='donation',
            name='recipient',
            field=models.ForeignKey(related_name='getter', to='nadc.Entity'),
        ),
        migrations.AlterField(
            model_name='expenditure',
            name='committee',
            field=models.ForeignKey(to='nadc.Entity'),
        ),
        migrations.AlterField(
            model_name='loan',
            name='committee',
            field=models.ForeignKey(to='nadc.Entity'),
        ),
    ]
