# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0002_candidate_govslug'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdditionalInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('canonical', models.CharField(max_length=20)),
                ('mugshot', models.ImageField(upload_to=b'/home/omaha/webapps/media/nadc/mugs/')),
                ('title', models.CharField(max_length=120)),
                ('description', models.TextField(null=True, blank=True)),
            ],
        ),
    ]
