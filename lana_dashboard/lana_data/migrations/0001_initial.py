# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-28 15:16
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AutonomousSystem',
            fields=[
                ('as_number', models.IntegerField(primary_key=True, serialize=False)),
                ('fqdn', models.CharField(max_length=255)),
                ('comment', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('code', models.CharField(max_length=8)),
                ('owners', models.ManyToManyField(related_name='institutions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='IPv4Subnet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('network_address', models.GenericIPAddressField(protocol='IPv4')),
                ('subnet_bits', models.IntegerField()),
                ('dns_server', models.GenericIPAddressField(protocol='IPv4')),
                ('comment', models.CharField(max_length=255)),
                ('institution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ipv4_subnets', to='lana_data.Institution')),
            ],
        ),
        migrations.AddField(
            model_name='autonomoussystem',
            name='institution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='autonomous_systems', to='lana_data.Institution'),
        ),
        migrations.AlterUniqueTogether(
            name='ipv4subnet',
            unique_together=set([('network_address', 'subnet_bits')]),
        ),
    ]