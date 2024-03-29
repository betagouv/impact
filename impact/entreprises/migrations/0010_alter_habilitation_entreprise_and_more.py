# Generated by Django 4.1.7 on 2023-03-07 10:32
import django.db.models.deletion
from django.conf import settings
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("entreprises", "0009_habilitation_confirmed_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="habilitation",
            name="entreprise",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="entreprises.entreprise",
            ),
        ),
        migrations.AlterField(
            model_name="habilitation",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
