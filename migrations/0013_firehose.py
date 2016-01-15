# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0012_additionalinfo_associated'),
    ]

    operations = [
        migrations.CreateModel(
            name='Firehose',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('cash', models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)),
                ('inkind', models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)),
                ('pledge', models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)),
                ('inkind_desc', models.TextField(null=True, blank=True)),
                ('donation_date', models.DateField(null=True, blank=True)),
                ('donation_year', models.CharField(default=b'', max_length=4)),
                ('week', models.CharField(max_length=10, null=True, blank=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('donor_name', models.CharField(max_length=200, null=True, blank=True)),
                ('source_table', models.CharField(max_length=10, null=True, blank=True)),
                ('donor', models.ForeignKey(related_name='firehose_giver', blank=True, to='nadc.Entity', null=True)),
                ('recipient', models.ForeignKey(related_name='firehose_getter', blank=True, to='nadc.Entity', null=True)),
            ],
        ),
    ]
