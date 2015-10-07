# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0007_candidate'),
    ]

    operations = [
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lender_name', models.CharField(max_length=70)),
                ('lender_addr', models.CharField(max_length=70)),
                ('loan_date', models.DateField()),
                ('loan_amount', models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)),
                ('loan_repaid', models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)),
                ('loan_forgiven', models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)),
                ('paid_by_third_party', models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)),
                ('guarantor', models.CharField(max_length=70, blank=True)),
                ('committee', models.ForeignKey(to='nadc.Getter')),
            ],
        ),
    ]
