# Generated by Django 4.2 on 2023-06-22 14:39
import django.utils.timezone
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("metabase", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="habilitation",
            name="ajoutee_le",
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="habilitation",
            name="modifiee_le",
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
