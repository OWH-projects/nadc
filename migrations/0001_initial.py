# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ballot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ballot', models.CharField(max_length=80)),
                ('ballot_type', models.CharField(max_length=5)),
                ('stance', models.CharField(max_length=10, null=True, blank=True)),
                ('notes', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cand_id', models.CharField(max_length=40)),
                ('cand_name', models.CharField(max_length=70, null=True, blank=True)),
                ('stance', models.CharField(max_length=2, null=True, blank=True)),
                ('office_govt', models.CharField(max_length=100, null=True, blank=True)),
                ('office_title', models.CharField(max_length=100, null=True, blank=True)),
                ('office_dist', models.CharField(max_length=100, null=True, blank=True)),
                ('donor_id', models.CharField(max_length=30, null=True, blank=True)),
                ('notes', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Donation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cash', models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)),
                ('inkind', models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)),
                ('pledge', models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)),
                ('inkind_desc', models.TextField(null=True, blank=True)),
                ('donation_date', models.DateField()),
                ('donation_year', models.CharField(default=b'', max_length=4)),
                ('stance', models.CharField(max_length=10, null=True, blank=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('donor_name', models.CharField(max_length=200, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('nadcid', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('canonical', models.CharField(max_length=10, null=True, blank=True)),
                ('name', models.CharField(max_length=80)),
                ('standard_name', models.CharField(max_length=80)),
                ('address', models.CharField(max_length=75, null=True, blank=True)),
                ('city', models.CharField(max_length=40, null=True, blank=True)),
                ('state', models.CharField(max_length=40, null=True, blank=True)),
                ('zip', models.CharField(max_length=20, null=True, blank=True)),
                ('entity_type', models.CharField(max_length=15, null=True, blank=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('occupation', models.TextField(null=True, blank=True)),
                ('employer', models.TextField(null=True, blank=True)),
                ('place_of_business', models.TextField(null=True, blank=True)),
                ('dissolved_date', models.DateField(null=True, blank=True)),
                ('registered_date', models.DateField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Expenditure',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('raw_target', models.CharField(max_length=100, null=True, blank=True)),
                ('payee', models.CharField(max_length=70, null=True, blank=True)),
                ('payee_addr', models.CharField(max_length=70)),
                ('exp_date', models.DateField()),
                ('exp_purpose', models.CharField(max_length=200)),
                ('amount', models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)),
                ('in_kind', models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)),
                ('stance', models.CharField(max_length=10, null=True, blank=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('committee_exp_name', models.CharField(max_length=200, null=True, blank=True)),
                ('committee', models.ForeignKey(related_name='committee_exp', blank=True, to='nadc.Entity', null=True)),
                ('payee_committee', models.ForeignKey(related_name='committee_payee', blank=True, to='nadc.Entity', null=True)),
                ('target_candidate', models.ForeignKey(related_name='committee_target_candidate', blank=True, to='nadc.Candidate', null=True)),
                ('target_committee', models.ForeignKey(related_name='committee_target_committee', blank=True, to='nadc.Entity', null=True)),
            ],
        ),
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
                ('guarantor', models.CharField(max_length=70, null=True, blank=True)),
                ('stance', models.CharField(max_length=10, null=True, blank=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('committee', models.ForeignKey(related_name='committee_lendee', blank=True, to='nadc.Entity', null=True)),
                ('lending_committee', models.ForeignKey(related_name='committee_lender', blank=True, to='nadc.Entity', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='donation',
            name='donor',
            field=models.ForeignKey(related_name='giver', blank=True, to='nadc.Entity', null=True),
        ),
        migrations.AddField(
            model_name='donation',
            name='recipient',
            field=models.ForeignKey(related_name='getter', blank=True, to='nadc.Entity', null=True),
        ),
        migrations.AddField(
            model_name='candidate',
            name='committee',
            field=models.ForeignKey(related_name='candidate_detail', to='nadc.Entity'),
        ),
        migrations.AddField(
            model_name='ballot',
            name='nadcid',
            field=models.ForeignKey(to='nadc.Entity'),
        ),
    ]
