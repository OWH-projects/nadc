# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadc', '0024_expenditure_payee_committee'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='expenditure',
            name='issue',
        ),
    ]
