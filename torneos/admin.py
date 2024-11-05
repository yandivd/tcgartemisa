from django.contrib import admin
from .models import *
# Register your models here.
class PlayerAdmin(admin.ModelAdmin):
    list_display=['user','victorys', 'defeats', 'ptos']

class TournamentPlayerAdmin(admin.ModelAdmin):
    list_display=['jugador', 'victorys', 'defeats', 'draws','byes', 'ptos','OMW', 'PGW', 'OGW']

class TopPlayerAdmin(admin.ModelAdmin):
    list_display=['player','position']

admin.site.register(Deck)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Tournament)
admin.site.register(TournamentPlayer, TournamentPlayerAdmin)
admin.site.register(TopPlayer, TopPlayerAdmin)
admin.site.register(Round)
admin.site.register(Emparents)
