# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-05-21 13:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('himalaya', '0030_auto_20170509_1528'),
    ]

    operations = [
        migrations.AddField(
            model_name='traveldata',
            name='mileage',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='\u91cc\u7a0b'),
        ),
    ]
