# Generated by Django 5.1.2 on 2024-12-17 18:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("torneos", "0014_emparents_final"),
    ]

    operations = [
        migrations.RenameField(
            model_name="topplayer",
            old_name="player",
            new_name="tournament_player",
        ),
        migrations.RenameField(
            model_name="tournament",
            old_name="players",
            new_name="tournament_players",
        ),
    ]