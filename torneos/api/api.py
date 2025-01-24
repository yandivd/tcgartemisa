from collections import defaultdict
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from torneos.models import *
from .serializers import *
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User

class CustomAuthTokenView(APIView):
    def post(self, request, *args, **kwargs):
        # Obtener el 'username' o 'email' y 'password' del request
        identifier = request.data.get('username')
        password = request.data.get('password')

        # Determinar si el 'identifier' es un email o un nombre de usuario
        if '@' in identifier:
            # Si parece un email, intentar autenticar con email
            user = authenticate(email=identifier, password=password)
        else:
            # Si no es un email, intentar autenticar con nombre de usuario
            user = authenticate(username=identifier, password=password)

        if user is not None:
            # Generar tokens JWT
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token

            access_exp = access.payload['exp']
            # Devolver los tokens en la respuesta
            return JsonResponse({
                'refresh': str(refresh),    
                'access': str(access),
                'access_exp': access_exp,
                'user_id': user.id,
                'username': user.username,
                'is_superuser': user.is_superuser
            }, status=200)
        else:
            return Response({'error':{'errorCode':101,'message': 'Invalid credentials'}, 'detail':'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
class VerifyTokenView(APIView):
    def post(self, request, *args, **kwargs):
        access_token = request.data.get('access')
        refresh_token = request.data.get('refresh')

        if not access_token and not refresh_token:
            return Response({'detail': 'Access token and refresh token are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar el token de acceso
        access_valid = False
        access_error = None
        if access_token:
            try:
                AccessToken(access_token)  # Esto lanzará un error si el token no es válido
                access_valid = True
            except TokenError as e:
                access_valid = False
                access_error = str(e)

        # Verificar el token de refresh
        refresh_valid = False
        refresh_error = None
        if refresh_token:
            try:
                RefreshToken(refresh_token)  # Esto lanzará un error si el token no es válido
                refresh_valid = True
            except TokenError as e:
                refresh_valid = False
                refresh_error = str(e)

        response_data = {
            'access_valid': access_valid,
            'refresh_valid': refresh_valid,
        }

        if not access_valid and not refresh_valid:
            return Response({'refresh_valid': False, 'access_valid': False}, status=status.HTTP_401_UNAUTHORIZED)

        if not access_valid and refresh_valid:
            # Si el token de refresh es válido, generar un nuevo token de acceso
            try:
                refresh = RefreshToken(refresh_token)
                new_access = str(refresh.access_token)
                response_data['new_access'] = new_access
                return Response(response_data, status=status.HTTP_200_OK)
            except TokenError as e:
                return Response({'detail': 'Refresh token is invalid', 'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(response_data, status=status.HTTP_200_OK)
##########################
###                    ###
##########################
def update_player_points(tournament):
    num_players = tournament.players.count()

    # Definir puntos base para cada rango de eliminación
    points_distribution = {
        'winner': 10,
        'finalist': 8,
        'thirdfinalist': 7,
        'semifinalist': 6,
        'quarterfinalist': 4,
        'participant': 1
    }

    # Ajustar puntos según el tamaño del torneo
    if num_players > 30:
        scale_factor = 1.5
    elif num_players > 20:
        scale_factor = 1.3
    else:
        scale_factor = 1.0

    for tournament_player in tournament.players.all():
        player = tournament_player.jugador
        
        # Contar torneos jugados por el jugador
        tj = TournamentPlayer.objects.filter(jugador=player).count()
        
        # Inicializar puntos acumulados
        total_points = 0

        # Asignar puntos según el rendimiento en el torneo actual
        if tournament.first_place and player == tournament.first_place.jugador:
            total_points += int(points_distribution['winner'] * scale_factor)

        elif tournament.second_place and player == tournament.second_place.jugador:
            total_points += int(points_distribution['finalist'] * scale_factor)

        elif tournament.third_place and player == tournament.third_place.jugador:
            total_points += int(points_distribution['thirdfinalist'] * scale_factor)

        elif tournament.top_players_4.filter(player=tournament_player).exists():
            total_points += int(points_distribution['semifinalist'] * scale_factor)

        elif tournament.top_players_8.filter(player=tournament_player).exists():
            total_points += int(points_distribution['quarterfinalist'] * scale_factor)

        else:
            total_points += int(points_distribution['participant'] * scale_factor)

        # Calcular bonificación por participación
        participation_bonus = 2 * tj  # Bonificación de 2 puntos por cada torneo jugado
        total_points += participation_bonus

        # Actualizar puntos del jugador
        player.ptos += total_points / (tj + 1)  # Dividir por (tj + 1) para evitar división por cero
        player.victorys += tournament_player.victorys
        player.defeats += tournament_player.defeats
        player.draws += tournament_player.draws

        player.save()

##########################
###                    ###
##########################

@api_view(['GET'])
def tournament_api(request):
    tournaments = Tournament.objects.all()
    serializer = TournamentSerializer(tournaments, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
def tournament_detail_api(request, id):
    tournament = Tournament.objects.get(id=id)
    serializer = TournamentSerializer(tournament)
    return JsonResponse(serializer.data, safe=False)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def inscribe_player_api(request, id_tournament):
    if request.method == 'POST':
        try:
            tournament = Tournament.objects.get(id=id_tournament)
        except Tournament.DoesNotExist:
            return JsonResponse({'error': 'Tournament not found'}, status=status.HTTP_404_NOT_FOUND)

        if tournament.status == 'Started' or tournament.status == 'Finished':
            return Response({'error':{'errorCode':203,'message': 'Tournament is already started'}, 'detail':'Tournament is already started'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.get(id=request.data.get('user'))
        try:
            player = Player.objects.get(user=user)
        except Player.DoesNotExist:
            return JsonResponse({'error': 'Player not found'}, status=status.HTTP_404_NOT_FOUND)

        deck_id = request.data.get('deck')
        if not deck_id:
            return JsonResponse({'error': 'Deck ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            deck = Deck.objects.get(id=deck_id)
        except Deck.DoesNotExist:
            return JsonResponse({'error': 'Deck not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Verificar si el jugador ya está registrado en el torneo
        if TournamentPlayer.objects.filter(jugador=player, tournament=tournament).exists():
            return Response({'error':{'errorCode':201,'message': 'Already Inscribed'}, 'detail':'Already Inscribed'}, status=status.HTTP_400_BAD_REQUEST)
        
        decklist_file = request.FILES.get('decklist')
        if decklist_file:
            img = Image.open(decklist_file)
            output = BytesIO()
            img.save(output, format='WEBP')
            output.seek(0)
            decklist_file = InMemoryUploadedFile(output, 'ImageField', f"{decklist_file.name.split('.')[0]}.webp", 'image/webp', output.getbuffer().nbytes, None)

        # Crear la inscripción del jugador en el torneo
        player_tournament = TournamentPlayer.objects.create(
            deck=deck,
            jugador=player,
            decklist=decklist_file,
            tournament=tournament
        )
        serializer = PlayerTournamentSerializer(player_tournament)
        tournament.tournament_players.add(player_tournament)
        
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unsubscribe_player(request, player_id):
    try:
        tournament_player = TournamentPlayer.objects.get(id=player_id)
    except TournamentPlayer.DoesNotExist:
        return JsonResponse({'error': {'errorCode': 202, 'message': 'Player not found'}}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'error': {'errorCode': 500, 'message': 'Internal server error'}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if request.method == 'POST':
        tournament_player.delete()
        return JsonResponse({'message': 'Player unsubscribed successfull'}, status=status.HTTP_200_OK)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_tournament_api(request, id_tournament):
    if request.method == 'POST':
        try:
            tournament = Tournament.objects.get(id=id_tournament)
        except Tournament.DoesNotExist:
            return JsonResponse({'error': 'Tournament not found'}, status=status.HTTP_404_NOT_FOUND)

        if tournament.status == 'Started':
            return JsonResponse({'error': 'Tournament is already started'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            tournament.stablish_rounds()
            tournament.stablish_top()
            tournament.status = 'Started'
            tournament.save()
            return JsonResponse({'message': 'Tournament started successfully', 'tournament_top':tournament.top, 'next_round':1}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'error': str(e)}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtain_players_orders_by_tournament(request, id_tournament):
    try:
        tournament = Tournament.objects.get(id=id_tournament)
    except Tournament.DoesNotExist:
        return JsonResponse({'message': 'Tournament not found'}, status=status.HTTP_404_NOT_FOUND)

    players = tournament.tournament_players.all().order_by('-ptos', '-PMW','-OMW', '-PGW', '-OGW')
    player_serializer = PlayerTournamentSerializer(players, many=True)
    return JsonResponse(player_serializer.data, safe=False, status=status.HTTP_200_OK)

def obtain_bye(player_list):
    last_player = None
    for player in reversed(player_list):
        if player.byes == 0:
            last_player = player
            player.byes += 1
            player.ptos += 3
            player.save()
            player_list = [p for p in player_list if p.id != player.id]
            break
    return player_list
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def obtain_next_round(request, id_tournament):
    if request.method == 'POST':
        try:
            tournament = Tournament.objects.get(id=id_tournament)
        except Tournament.DoesNotExist:
            return JsonResponse({'message': 'Tournament not found'}, status=status.HTTP_404_NOT_FOUND)
        
        next_round = tournament.rounds.filter(finished=False).order_by('no_round').first()
        if not next_round:
            print('Ya es pal top')
            if tournament.top == 8:
                print('Es top 8')
                print(tournament.top_players_8)
                if not tournament.top_players_8.exists():
                    print('Es la ronda top 8')
                    return create_top_8(tournament)
                elif not tournament.top_players_4.exists():
                    print('Es la ronda del top 4')
                    return create_top_4(tournament)
                elif not tournament.final.exists():
                    print('Es la ronda final')
                    return create_final(tournament)
                else:
                    return finalize_tournament(tournament)
            elif tournament.top == 4:
                print('Es top 4')
                if not tournament.top_players_4.exists():
                    return create_top_4(tournament)
                elif not tournament.final.exists():
                    return create_final(tournament)
                else:
                    return finalize_tournament(tournament)
            else:
                return JsonResponse({'message': 'No unfinished rounds available'}, status=status.HTTP_200_OK)
        
        return create_regular_round(tournament, next_round)

def create_top_8(tournament):
    print('Se juega top 8')
    top_players = tournament.players.all().order_by('-ptos', '-PMW', '-OMW', '-PGW', '-OGW')[:8]
    positions = {0: 1, 1: 8, 2: 5, 3: 4, 4: 3, 5: 6, 6: 7, 7: 2}
    for index, player in enumerate(top_players):
        top_player = TopPlayer.objects.create(player=player, position=positions[index])
        tournament.top_players_8.add(top_player)
    
    next_round = Round.objects.create(no_round=tournament.rounds.count() + 1)
    tournament.rounds.add(next_round)
    top_players = tournament.top_players_8.all().order_by('position')
    matches = []

    for i in range(0, len(top_players), 2):
        if i + 1 < len(top_players):
            match = Emparents(
                player1=top_players[i].player,
                player2=top_players[i + 1].player,
                top=True
            )
            matches.append(match)
    
    emparents = Emparents.objects.bulk_create(matches)
    next_round.emparents.add(*emparents)
    next_round.finished = True
    next_round.save()
    
    next_round_serializer = RoundSerializer(next_round)
    return JsonResponse(next_round_serializer.data, safe=False, status=status.HTTP_201_CREATED)

def create_top_4(tournament):
    
    print('Se juega top 4')
    if not tournament.top_players_8.exists():
        top_players = tournament.players.all().order_by('-ptos','-PMW', '-OMW', '-PGW', '-OGW')[:4]
        positions = {0: 1, 1: 4, 2: 3, 3: 2}
        for index, player in enumerate(top_players):
            top_player = TopPlayer.objects.create(player=player, position=positions[index])
            tournament.top_players_4.add(top_player)
        
        next_round = Round.objects.create(no_round=tournament.rounds.count() + 1)
        tournament.rounds.add(next_round)
        top_players = tournament.top_players_4.all().order_by('position')
        matches = []
        
        for i in range(0, len(top_players), 2):
            if i + 1 < len(top_players):
                match = Emparents(player1=top_players[i].player, player2=top_players[i + 1].player, top=True)
                matches.append(match)
        
        emparents = Emparents.objects.bulk_create(matches)
        next_round.emparents.add(*emparents)
        next_round.finished = True
        next_round.save()
        
        next_round_serializer = RoundSerializer(next_round)
        return JsonResponse(next_round_serializer.data, safe=False, status=status.HTTP_201_CREATED)
    else:
        top_players = tournament.top_players_8.all().order_by('position')
        winners = []

        for i in range(0, len(top_players), 2):
            if i + 1 < len(top_players):
                player1 = top_players[i].player
                player2 = top_players[i + 1].player
                last_match = Emparents.objects.filter(
                    (models.Q(player1=player1) & models.Q(player2=player2)) |
                    (models.Q(player1=player2) & models.Q(player2=player1)),
                    top=True
                ).order_by('-id').first()
                
                if last_match:
                    winner = last_match.player1 if last_match.result_ply1 > last_match.result_ply2 else last_match.player2
                    winners.append((winner, min(top_players[i].position, top_players[i+1].position)))

        winners.sort(key=lambda x: x[1])
        next_round = Round.objects.create(no_round=tournament.rounds.count() + 1)
        tournament.rounds.add(next_round)
        
        matches = [
            Emparents(player1=winners[0][0], player2=winners[1][0], top=True),
            Emparents(player1=winners[2][0], player2=winners[3][0], top=True)
        ]
        
        emparents = Emparents.objects.bulk_create(matches)
        next_round.emparents.add(*emparents)
        next_round.finished = True
        next_round.save()
        
        positions = {0: 1, 1: 2, 2: 3, 3: 4}
        for index, (winner, _) in enumerate(winners):
            top_player = TopPlayer.objects.create(player=winner, position=positions[index])
            tournament.top_players_4.add(top_player)
        
        next_round_serializer = RoundSerializer(next_round)
        return JsonResponse(next_round_serializer.data, safe=False, status=status.HTTP_201_CREATED)

def create_final(tournament):
    print('Se juega la final')
    top_players = tournament.top_players_4.all().order_by('position')
    tournament.final.add(*top_players)

    winners = []
    losers = []

    for i in range(0, len(top_players), 2):
        if i + 1 < len(top_players):
            player1 = top_players[i].player
            player2 = top_players[i + 1].player
            last_match = Emparents.objects.filter(
                (models.Q(player1=player1) & models.Q(player2=player2)) |
                (models.Q(player1=player2) & models.Q(player2=player1)),
                top=True
            ).order_by('-id').first()
            
            if last_match:
                if last_match.result_ply1 > last_match.result_ply2:
                    winners.append(top_players[i])
                    losers.append(top_players[i + 1])
                else:
                    winners.append(top_players[i + 1])
                    losers.append(top_players[i])

    winners.sort(key=lambda x: x.position)
    losers.sort(key=lambda x: x.position)
    next_round = Round.objects.create(no_round=tournament.rounds.count() + 1)
    tournament.rounds.add(next_round)
    
    matches = [
        Emparents(player1=winners[0].player, player2=winners[1].player, top=True, final='final'),
        Emparents(player1=losers[0].player, player2=losers[1].player, top=True, final='bythird')
    ]
    
    emparents = Emparents.objects.bulk_create(matches)
    next_round.emparents.add(*emparents)
    next_round.finished = True
    next_round.save()
    
    next_round_serializer = RoundSerializer(next_round)
    return JsonResponse(next_round_serializer.data, safe=False, status=status.HTTP_201_CREATED)

def finalize_tournament(tournament):
    print('Finalizando el torneo')
    # final_players = tournament.final.all().values_list('player', flat=True)
    final_match = Emparents.objects.filter(
        final='final',
        top=True
    ).order_by('-id').first()

    # top_4_players = tournament.top_players_4.all().values_list('player', flat=True)
    third_place_match = Emparents.objects.filter(
        final='bythird',
        top=True
    ).exclude(id=final_match.id).order_by('-id').first()

    if final_match and third_place_match:
        if final_match.result_ply1 > final_match.result_ply2:
            tournament.first_place = final_match.player1
            tournament.second_place = final_match.player2
        else:
            tournament.first_place = final_match.player2
            tournament.second_place = final_match.player1

        if third_place_match.result_ply1 > third_place_match.result_ply2:
            tournament.third_place = third_place_match.player1
        else:
            tournament.third_place = third_place_match.player2

        tournament.status = "Finished"
        tournament.save()

        update_player_points(tournament)

        return JsonResponse({
            'message': 'Torneo finalizado',
            'first_place': tournament.first_place.jugador.user.username,
            'second_place': tournament.second_place.jugador.user.username,
            'third_place': tournament.third_place.jugador.user.username
        }, status=status.HTTP_200_OK)

def create_regular_round(tournament, next_round):
    players_ordered = tournament.players.all().order_by('-ptos')
    if players_ordered.count() % 2 != 0:
        if next_round.no_round == 1:
            import random
            players_ordered = list(players_ordered)
            random.shuffle(players_ordered)
        players_ordered = obtain_bye(players_ordered)

    grouped_players = defaultdict(list)
    for player in players_ordered:
        grouped_players[player.ptos].append(player)

    matches = []

    # Emparejar jugadores dentro de cada grupo
    previous_group_remainder = None
    for points, group in sorted(grouped_players.items(), reverse=True):
        random.shuffle(group)  # Barajar el grupo

        if previous_group_remainder:
            group.insert(0, previous_group_remainder)  # Añadir el jugador sobrante del grupo anterior

        i = 0
        while i < len(group) - 1:
            player1 = group[i]
            player2 = group[i + 1]
            
            has_played_before = has_played_before(tournament, player1, player2)

            if not has_played_before:
                match = Emparents(player1=player1, player2=player2)
                matches.append(match)
                i += 2
            else:
                # Si ya jugaron, barajar el grupo nuevamente
                random.shuffle(group)
                i = 0

        # Si hay un jugador sobrante, guardarlo para el siguiente grupo
        if i == len(group) - 1:
            previous_group_remainder = group[i]
        else:
            previous_group_remainder = None
    
    emparents = Emparents.objects.bulk_create(matches)
    next_round.emparents.add(*emparents)
    next_round.finished = True
    next_round.save()
    
    next_round_serializer = RoundSerializer(next_round)
    return JsonResponse(next_round_serializer.data, safe=False, status=status.HTTP_201_CREATED)

def calculate_omw(player):
    opponents = player.get_opponents()
    total_opponent_mwp = 0
    count = 0

    for opponent in opponents:
        max_points = (opponent.victorys + opponent.draws + opponent.defeats) * 3
        opponent_mwp = max(opponent.ptos / max_points, 0.33) if max_points > 0 else 0.33
        total_opponent_mwp += opponent_mwp
        count += 1

    return total_opponent_mwp / count if count > 0 else 0.33

def calculate_pgw(player):
    # Obtener todos los emparejamientos del jugador
    matches = Emparents.objects.filter(
        models.Q(player1=player) | models.Q(player2=player)
    )
    
    total_game_points = 0
    total_games = 0

    for match in matches:
        if match.player1 == player:
            total_game_points += match.result_ply1 * 3
            total_games += (match.result_ply1 + match.result_ply2) * 3
        else:
            total_game_points += match.result_ply2 * 3
            total_games += (match.result_ply1 + match.result_ply2) * 3

    return total_game_points / total_games if total_games > 0 else 0.33

def calculate_pmw(player):
    total_matches = player.victorys + player.draws + player.defeats
    pmw = (player.victorys / total_matches) if total_matches > 0 else 0
    return pmw

def calculate_ogw(player):
    opponents = player.get_opponents()
    total_opponent_gwp = 0
    count = 0

    for opponent in opponents:
        matches = Emparents.objects.filter(
            models.Q(player1=opponent) | models.Q(player2=opponent)
        )
        total_game_points = sum(
            (match.result_ply1 if match.player1 == opponent else match.result_ply2) * 3
            for match in matches
        )
        total_games = sum(
            (match.result_ply1 + match.result_ply2) * 3
            for match in matches
        )
        opponent_gwp = max(total_game_points / total_games, 0.33) if total_games > 0 else 0.33
        total_opponent_gwp += opponent_gwp
        count += 1

    return total_opponent_gwp / count if count > 0 else 0.33

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stablish_result_emparents(request, id_emparent):
    try:
        emparent = Emparents.objects.get(id=id_emparent)
    except Emparents.DoesNotExist:
        return JsonResponse({'message': 'Match not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        result_ply1 = request.data.get('result_ply1')
        result_ply2 = request.data.get('result_ply2')
        player1 = emparent.player1
        player2 = emparent.player2

        # Determinar el tipo de partido basado en las posiciones
        if emparent.top:
            match_type = 'Clasificatoria'
        else:
            match_type = 'Regular'

        if match_type == 'Regular':
            if result_ply1 > result_ply2:
                player1.ptos += 3
                player1.victorys += 1
                player2.defeats += 1
            elif result_ply1 < result_ply2:
                player2.ptos += 3
                player2.victorys += 1
                player1.defeats += 1
            else:
                player1.draws += 1
                player1.ptos += 1
                player2.draws += 1
                player2.ptos += 1

            # Calcular estadísticas para ambos jugadores
            for player in [player1, player2]:
                player.OMW = calculate_omw(player)
                player.PGW = calculate_pgw(player)
                player.OGW = calculate_ogw(player)
                player.PMW = calculate_pmw(player)
                player.save()

        else:
            if result_ply1 > result_ply2:
                player1.victorys += 1
                player2.defeats += 1
            elif result_ply1 < result_ply2:
                player2.victorys += 1
                player1.defeats += 1

            player1.save()
            player2.save()

        emparent.result_ply1 = result_ply1
        emparent.result_ply2 = result_ply2
        emparent.save()

        emparent_serializer = EmparentsSerializers(emparent)
        return JsonResponse(emparent_serializer.data, safe=False, status=status.HTTP_201_CREATED)

    return JsonResponse({'message': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def decks_api_views(request):
    decks = Deck.objects.all()
    decks_serializer = DeckSerializer(decks, many=True)
    return JsonResponse(decks_serializer.data, safe=False, status=status.HTTP_200_OK)

def rest_tournament(request, id):
    try:
        torneo = Tournament.objects.get(id=id)
    except Tournament.DoesNotExist:
        print("Torneo no encontrado")
        return

    # Eliminar rondas
    for ronda in torneo.rounds.all():
        ronda.delete()

    # Eliminar emparentes asociados a las rondas
    for emparente in Emparents.objects.filter(round__in=torneo.rounds.all()):
        emparente.delete()

    torneo.status = 'Created'
    torneo.save()

    # print("Rondas eliminadas con éxito")
    return JsonResponse('Eliminado con exito', safe=False)
        