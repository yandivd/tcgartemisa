from rest_framework import serializers
from torneos.models import *
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

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
    players = PlayerTournamentSerializer(many=True)
    class Meta:
        model = Tournament
        fields = '__all__' 

