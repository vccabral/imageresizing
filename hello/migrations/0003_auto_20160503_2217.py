# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-03 22:17
from __future__ import unicode_literals

from django.db import migrations, models
from hello.swatches import swatch_list
from django.utils.encoding import smart_unicode

def create_swatches(apps, schema_editor):
	Swatch = apps.get_model("hello", "Swatch")
	for swatch in swatch_list:
		swatch_instance = Swatch(
			name = smart_unicode(swatch[1], encoding='latin-1', strings_only=False, errors='strict'),
			red = swatch[0][0],
			green = swatch[0][1],
			blue = swatch[0][2]
		).save()

class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0002_swatch'),
    ]

    operations = [
    	migrations.RunPython(create_swatches),
    ]
