# Generated by Django 5.1.2 on 2024-11-04 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('torneos', '0012_emparents_top'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='final',
            field=models.ManyToManyField(blank=True, related_name='final', to='torneos.topplayer'),
        ),
    ]
