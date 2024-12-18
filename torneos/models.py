from django.db import models
from django.contrib.auth.models import User

class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ptos = models.IntegerField(default=0)
    victorys = models.IntegerField(default=0)
    defeats = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.username
    
class Deck(models.Model):
    name = models.CharField(max_length=150)
    img = models.ImageField(upload_to='decks')

    def __str__(self):
        return self.name

class TournamentPlayer(models.Model):
    jugador = models.ForeignKey(Player, on_delete=models.CASCADE)
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, blank=True, null=True)
    decklist = models.ImageField(upload_to='decklists', blank=True, null=True)
    ptos = models.IntegerField(default=0)
    victorys = models.IntegerField(default=0)
    defeats = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    byes = models.IntegerField(default=0)
    PMW = models.DecimalField(decimal_places=2, max_digits=5, blank=True, null=True, default=0.00)    
    OMW = models.DecimalField(decimal_places=2, max_digits=5, blank=True, null=True, default=0.00)    
    PGW = models.DecimalField(decimal_places=2, max_digits=5, blank=True, null=True, default=0.00)    
    OGW = models.DecimalField(decimal_places=2, max_digits=5, blank=True, null=True, default=0.00)
    
    def __str__(self):
        return self.jugador.user.username
    
    def get_opponents(self):
        # Obtener todos los partidos donde el jugador es player1
        matches_as_player1 = Emparents.objects.filter(player1=self)
        # Obtener todos los partidos donde el jugador es player2
        matches_as_player2 = Emparents.objects.filter(player2=self)

        # Obtener los oponentes de ambos conjuntos de partidos
        opponents_as_player1 = [match.player2 for match in matches_as_player1]
        opponents_as_player2 = [match.player1 for match in matches_as_player2]

        # Combinar y eliminar duplicados
        all_opponents = set(opponents_as_player1 + opponents_as_player2)
        return all_opponents
    
    def has_won_previous_round(self):
        # Obtener el último emparejamiento del jugador
        last_emparent = Emparents.objects.filter(
            models.Q(player1=self.player) | models.Q(player2=self.player)
        ).order_by('-round__no_round').first()

        if not last_emparent:
            return False

        # Determinar si el jugador ganó
        if last_emparent.player1 == self.player:
            return last_emparent.result_ply1 > last_emparent.result_ply2
        else:
            return last_emparent.result_ply2 > last_emparent.result_ply1

class Emparents(models.Model):
    player1 = models.ForeignKey(TournamentPlayer, related_name='Player1', on_delete=models.CASCADE)
    player2 = models.ForeignKey(TournamentPlayer, related_name='Player2', on_delete=models.CASCADE)
    result_ply1 = models.IntegerField(default=0)
    result_ply2 = models.IntegerField(default=0)
    top = models.BooleanField(default=False)
    final = models.CharField(max_length=150, default='round')

    def __str__(self):
        return self.player1.jugador.user.username + 'VS' +self.player2.jugador.user.username
    
class Round(models.Model):
    no_round = models.IntegerField(default=0)
    emparents = models.ManyToManyField(Emparents, blank=True)
    finished = models.BooleanField(default=False)

    def __str__(self):
        return str(self.no_round)
    
class TopPlayer(models.Model):
    tournament_player = models.ForeignKey(TournamentPlayer, on_delete=models.CASCADE)
    position = models.IntegerField(default=0)

    def __str__(self):
        return self.tournament_player.jugador.user.username
    
class Tournament(models.Model):
    date = models.DateTimeField()
    place = models.CharField(blank=True, null=True, max_length=50)
    address = models.CharField(max_length=150, blank=True, null=True)
    tournament_players = models.ManyToManyField(TournamentPlayer, blank=True)
    rounds = models.ManyToManyField(Round, blank=True)
    top = models.IntegerField(default=4)
    top_players_8 = models.ManyToManyField(TopPlayer, blank=True, related_name='top_8')
    top_players_4 = models.ManyToManyField(TopPlayer, blank=True, related_name='top_4')
    final = models.ManyToManyField(TopPlayer, blank=True, related_name='final')
    first_place = models.ForeignKey(TournamentPlayer, on_delete=models.CASCADE, blank=True, null=True, related_name='First_Place')
    second_place = models.ForeignKey(TournamentPlayer, on_delete=models.CASCADE, blank=True, null=True, related_name='Second_Place')
    third_place = models.ForeignKey(TournamentPlayer, on_delete=models.CASCADE, blank=True, null=True, related_name='Third_Place')
    status = models.CharField(max_length=150)

    def __str__(self):
        return str(self.date)
    
    def stablish_rounds(self):
        player_count = self.tournament_players.count()
        if 4 <= player_count < 8:
            rounds = 3
        elif 9 <= player_count < 16:
            rounds = 4
        elif 17 <= player_count < 32:
            rounds = 5
        elif 33 <= player_count < 64:
            rounds = 6
        elif 65 <= player_count < 128:
            rounds = 7
        elif player_count >= 129:
            rounds = 8
        else:
            rounds = 0

        for i in range(rounds):
            self.rounds.add(Round.objects.create(no_round=i+1))

    def stablish_top(self):
        self.top = 4 if self.tournament_players.count() < 15 else 8
        self.save()

    
    def stablish_top_8(self):
        top_players = self.tournament_players.order_by('-ptos')[:8]
        positions = {0: 1, 1: 8, 2: 5, 3: 4, 4: 3, 5: 6, 6: 7, 7: 2}

        for index, player in enumerate(top_players):
            top_player = TopPlayer.objects.create(player=player, position=positions[index])
            self.top_players_8.add(top_player)

    def stablish_top_4(self):
        if self.top == 4:
            top_players = self.tournament_players.order_by('-ptos')[:4]
            positions = {0: 1, 1: 4, 2: 3, 3: 2}

            for index, player in enumerate(top_players):
                top_player = TopPlayer.objects.create(player=player, position=positions[index])
                self.top_players_4.add(top_player)

    # def emparents(self):
    #     import random

    #     current_round = self.rounds.filter(emparents).order_by('no_round').first()
    #     if not current_round:
    #         return
            
    #     players = list(self.players.all())
    #     random.shuffle(players)
        
    #     if current_round.no_round == 1:
    #         if len(players) % 2 != 0:
    #             # Seleccionar jugador random para bye
    #             bye_player = random.choice(players)
    #             bye_player.ptos += 3
    #             bye_player.save()
    #             players.remove(bye_player)
    #             players.append(bye_player)
                
    #         # Emparejar jugadores
    #         for i in range(0, len(players)-1, 2):
    #             emparejamiento = Emparents.objects.create(
    #                 player1=players[i],
    #                 player2=players[i+1]
    #             )
    #             current_round.emparents.add(emparejamiento)  # Agregar a la ronda actual
    #     else:
    #         # Lógica para rondas posteriores
    #         # Ordenar jugadores por puntos
    #         players = list(self.players.order_by('-ptos'))
            
    #         if len(players) % 2 != 0:
    #             # Seleccionar último jugador para bye
    #             bye_player = players.pop()  # Remover el último jugador
    #             bye_player.ptos += 3
    #             bye_player.save()
            
    #         # Emparejar jugadores por orden de puntos
    #         for i in range(0, len(players), 2):
    #             emparejamiento = Emparents.objects.create(
    #                 player1=players[i],
    #                 player2=players[i+1]
    #             )
    #             current_round.emparents.add(emparejamiento)  # Agregar a la ronda actual
        