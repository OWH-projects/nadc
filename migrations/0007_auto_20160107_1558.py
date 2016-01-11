# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0006_auto_20151229_2104'),
    ]

    operations = [
        migrations.CreateModel(
            name='Misc',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('misc_name', models.CharField(max_length=150, null=True, blank=True)),
                ('misc_title', models.CharField(max_length=50, null=True, blank=True)),
                ('misc_address', models.CharField(max_length=150, null=True, blank=True)),
                ('misc_phone', models.CharField(max_length=50, null=True, blank=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('committee', models.ForeignKey(related_name='misc_peeps', to='nadc.Entity')),
            ],
        ),
        migrations.RenameField(
            model_name='donation',
            old_name='stance',
            new_name='week',
        ),
    ]
