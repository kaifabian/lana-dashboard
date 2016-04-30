# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-30 22:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lana_data', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tunnel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('protocol', models.CharField(choices=[('fastd', 'Fastd tunnel'), ('other', 'Other')], max_length=5, verbose_name='Protocol')),
                ('mode', models.CharField(choices=[('tun', 'tun'), ('tap', 'tap')], max_length=3, verbose_name='Mode')),
                ('comment', models.CharField(blank=True, max_length=255, null=True, verbose_name='Comment')),
                ('encryption_method', models.CharField(blank=True, max_length=255, null=True, verbose_name='Encryption method')),
                ('mtu', models.IntegerField(blank=True, null=True, verbose_name='MTU')),
            ],
        ),
        migrations.CreateModel(
            name='TunnelEndpoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_ipv4', models.GenericIPAddressField(blank=True, null=True, protocol='IPv4', verbose_name='External IPv4 address')),
                ('internal_ipv4', models.GenericIPAddressField(blank=True, null=True, protocol='IPv4', verbose_name='Internal IPv4 address')),
                ('public_key', models.CharField(blank=True, max_length=255, null=True, verbose_name='Public key')),
                ('autonomous_system', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tunnel_endpoints', to='lana_data.AutonomousSystem', verbose_name='Autonomous System')),
            ],
        ),
        migrations.AddField(
            model_name='tunnel',
            name='endpoint1',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='tunnel1', to='lana_data.TunnelEndpoint', verbose_name='Endpoint 1'),
        ),
        migrations.AddField(
            model_name='tunnel',
            name='endpoint2',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='tunnel2', to='lana_data.TunnelEndpoint', verbose_name='Endpoint 2'),
        ),
    ]
