# Generated by Django 5.1.2 on 2024-11-03 22:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('torneos', '0006_round_finished'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournamentplayer',
            name='OGW',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='tournamentplayer',
            name='OMW',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='tournamentplayer',
            name='PGW',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='tournamentplayer',
            name='PMW',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=5, null=True),
        ),
    ]
