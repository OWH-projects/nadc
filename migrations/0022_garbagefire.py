# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0021_auto_20151028_1733'),
    ]

    operations = [
        migrations.CreateModel(
            name='GarbageFire',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('donor_name', models.CharField(max_length=130)),
                ('donor_address', models.CharField(max_length=130)),
                ('donor_city', models.CharField(max_length=130)),
                ('donor_state', models.CharField(max_length=80)),
                ('donor_zip', models.CharField(max_length=10)),
                ('donor_occupation', models.CharField(max_length=130)),
                ('donor_business', models.CharField(max_length=130)),
                ('donor_employer', models.CharField(max_length=130)),
                ('transaction_date', models.DateField(null=True, blank=True)),
                ('transaction_type', models.CharField(max_length=1)),
                ('recipient_name', models.CharField(max_length=130)),
                ('recipient_address', models.CharField(max_length=130)),
                ('amount', models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)),
                ('description', models.CharField(max_length=130)),
                ('notes', models.TextField(null=True, blank=True)),
                ('nadcid', models.ForeignKey(to='nadc.Entity')),
            ],
        ),
    ]
