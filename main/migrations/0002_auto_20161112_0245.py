# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-11-12 02:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='title',
            field=models.CharField(max_length=128),
        ),
    ]
