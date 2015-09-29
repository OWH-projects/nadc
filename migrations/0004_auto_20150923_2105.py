# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0003_remove_donation_intermediary'),
    ]

    operations = [
        migrations.RenameField(
            model_name='donation',
            old_name='donor',
            new_name='nadcid',
        ),
        migrations.AddField(
            model_name='giver',
            name='nadcid',
            field=models.CharField(default='fake', max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='giver',
            name='id',
            field=models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True),
        ),
    ]
