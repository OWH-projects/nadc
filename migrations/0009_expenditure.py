# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0008_loan'),
    ]

    operations = [
        migrations.CreateModel(
            name='Expenditure',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('payee', models.CharField(max_length=70)),
                ('payee_addr', models.CharField(max_length=70)),
                ('exp_date', models.DateField()),
                ('exp_purpose', models.CharField(max_length=200)),
                ('amount', models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)),
                ('in_kind', models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)),
                ('committee', models.ForeignKey(to='nadc.Getter')),
            ],
        ),
    ]
