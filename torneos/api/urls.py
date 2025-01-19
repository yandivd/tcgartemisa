from django.urls import path
from .. import views
from .api import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView #Esto es para la autenticacion original  

urlpatterns = [
    path("", views.index, name="index"),
    path('api/authenticate/', CustomAuthTokenView.as_view(), name='authenticate'),
    path('api/verify/', VerifyTokenView.as_view(), name='verify'),
    path("tournament_list/", tournament_api), #lista todos los torneos (GET)
    path("tournament/<int:id>/", tournament_detail_api), #lista todos los torneos (GET)
    path("inscribe_player/<int:id_tournament>/", inscribe_player_api), #recibe el deck y el decklist para inscribir un player (POST)
    path("unsubscribe_player/<int:player_id>/", unsubscribe_player), #recibe el deck y el decklist para inscribir un player (POST)
    path("start_tournament/<int:id_tournament>/", start_tournament_api), #inicia el torneo del id enviado (POST)
    path("obtain_players_orders_by_tournament/<int:id_tournament>/", obtain_players_orders_by_tournament), #obtener los players del torneo ordenados (GET)
    path("obtain_next_round/<int:id_tournament>/", obtain_next_round), #obtener la siguiente ronda (GET)
    path("stablish_result/<int:id_emparent>/", stablish_result_emparents), #definir los resultados de un emparejamiento

    path('api/decks/', decks_api_views), #obtener el listado de todos los deckss

    path('restart_tournament/<int:id>/', rest_tournament)

]
