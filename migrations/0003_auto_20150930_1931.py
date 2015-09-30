# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0002_auto_20150930_1931'),
    ]

    operations = [
        migrations.CreateModel(
            name='Donation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cash', models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)),
                ('inkind', models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)),
                ('pledge', models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)),
                ('inkind_desc', models.TextField(null=True, blank=True)),
                ('date', models.DateField()),
                ('source', models.CharField(max_length=5, choices=[(b'B1AB', b'B1AB'), (b'B2A', b'B2A'), (b'B3', b'B3'), (b'B4A', b'B4A'), (b'B5', b'B5')])),
            ],
        ),
        migrations.CreateModel(
            name='Getter',
            fields=[
                ('nadcid', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('canonical', models.CharField(max_length=10, null=True, blank=True)),
                ('name', models.CharField(max_length=65)),
                ('standard_name', models.CharField(max_length=65)),
                ('address', models.CharField(max_length=75, null=True, blank=True)),
                ('city', models.CharField(max_length=40, null=True, blank=True)),
                ('state', models.CharField(max_length=40, null=True, blank=True)),
                ('zip', models.CharField(max_length=20, null=True, blank=True)),
                ('recipient_type', models.CharField(max_length=15, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Giver',
            fields=[
                ('nadcid', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('canonical', models.CharField(max_length=10, null=True, blank=True)),
                ('name', models.CharField(max_length=65)),
                ('standard_name', models.CharField(max_length=65)),
                ('address', models.CharField(max_length=75, null=True, blank=True)),
                ('city', models.CharField(max_length=40, null=True, blank=True)),
                ('state', models.CharField(max_length=40, null=True, blank=True)),
                ('zip', models.CharField(max_length=20, null=True, blank=True)),
                ('contributor_type', models.CharField(max_length=15, null=True, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='donation',
            name='donor',
            field=models.ForeignKey(to='nadc.Giver'),
        ),
        migrations.AddField(
            model_name='donation',
            name='recipient',
            field=models.ForeignKey(to='nadc.Getter'),
        ),
    ]
