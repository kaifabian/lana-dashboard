# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-08 17:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lana_data', '0005_release'),
    ]

    operations = [
        migrations.AddField(
            model_name='tunnelendpoint',
            name='dynamic_ipv4',
            field=models.BooleanField(default=False, verbose_name='Dynamic IPv4 address'),
        ),
    ]