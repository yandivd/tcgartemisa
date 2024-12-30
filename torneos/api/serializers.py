from rest_framework import serializers
from torneos.models import *
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password']

class PlayerSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Player
        fields = '__all__'

class PlayerTournamentSerializer(serializers.ModelSerializer):
    jugador = PlayerSerializer()
    class Meta:
        model = TournamentPlayer
        fields = '__all__' 

class TopPlayerSerializer(serializers.ModelSerializer):
    tournament_player = PlayerTournamentSerializer()
    class Meta:
        model = TopPlayer
        fields = '__all__' 

class EmparentsSerializers(serializers.ModelSerializer):
    player1 = PlayerTournamentSerializer()
    player2 = PlayerTournamentSerializer()
    class Meta:
        model = Emparents
        fields = '__all__'

class RoundSerializer(serializers.ModelSerializer):
    emparents = EmparentsSerializers(many=True)
    class Meta:
        model = Round
        fields = '__all__'

class TournamentSerializer(serializers.ModelSerializer):
    rounds = RoundSerializer(many=True)
    tournament_players = PlayerTournamentSerializer(many=True)
    top_players_8 = TopPlayerSerializer(many=True)
    top_players_4 = TopPlayerSerializer(many=True)
    final = TopPlayerSerializer(many=True)
    class Meta:
        model = Tournament
        fields = '__all__' 

class TopPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopPlayer
        fields = '__all__' 

class DeckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deck
        fields = '__all__'

