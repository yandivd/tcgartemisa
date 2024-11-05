# Generated by Django 5.1.2 on 2024-11-03 01:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Deck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('img', models.ImageField(upload_to='decks')),
            ],
        ),
        migrations.CreateModel(
            name='Emparents',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result_ply1', models.IntegerField(default=0)),
                ('result_ply2', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='TopPlayer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ptos', models.IntegerField(default=0)),
                ('victorys', models.IntegerField(default=0)),
                ('defeats', models.IntegerField(default=0)),
                ('draws', models.IntegerField(default=0)),
                ('deleted', models.BooleanField(default=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Round',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('no_round', models.IntegerField(default=0)),
                ('emparents', models.ManyToManyField(to='torneos.emparents')),
            ],
        ),
        migrations.CreateModel(
            name='TournamentPlayer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('decklist', models.ImageField(blank=True, null=True, upload_to='decklists')),
                ('ptos', models.IntegerField(default=0)),
                ('victorys', models.IntegerField(default=0)),
                ('defeats', models.IntegerField(default=0)),
                ('draws', models.IntegerField(default=0)),
                ('byes', models.IntegerField(default=0)),
                ('PMW', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('OMW', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('PGW', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('OGW', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('deck', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='torneos.deck')),
                ('jugador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='torneos.player')),
            ],
        ),
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('top', models.IntegerField(default=4)),
                ('status', models.CharField(max_length=150)),
                ('rounds', models.ManyToManyField(to='torneos.round')),
                ('top_players', models.ManyToManyField(to='torneos.topplayer')),
                ('first_place', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='First_Place', to='torneos.tournamentplayer')),
                ('players', models.ManyToManyField(to='torneos.tournamentplayer')),
                ('second_place', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Second_Place', to='torneos.tournamentplayer')),
                ('third_place', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Third_Place', to='torneos.tournamentplayer')),
            ],
        ),
        migrations.AddField(
            model_name='topplayer',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='torneos.tournamentplayer'),
        ),
        migrations.AddField(
            model_name='emparents',
            name='player1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Player1', to='torneos.tournamentplayer'),
        ),
        migrations.AddField(
            model_name='emparents',
            name='player2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Player2', to='torneos.tournamentplayer'),
        ),
    ]
