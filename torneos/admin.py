from django.contrib import admin
from .models import *
from django.utils.html import format_html
# Register your models here.
class PlayerAdmin(admin.ModelAdmin):
    list_display=['user','victorys', 'defeats', 'ptos']

class TournamentPlayerAdmin(admin.ModelAdmin):
    list_display=['jugador', 'victorys', 'defeats', 'draws','byes', 'ptos','OMW', 'PGW', 'OGW']

class TopPlayerAdmin(admin.ModelAdmin):
    list_display=['tournament_player','position']

class DeckAmin(admin.ModelAdmin):
    list_display=['name', 'img']

    def imagen_tag(self, obj):
        if obj.imagen:
            return format_html(f'<img src="{obj.img.url}" width="50" height="50" style="object-fit: cover;" />')
        return "No hay imagen"
    imagen_tag.short_description = 'Imagen'

admin.site.register(Deck, DeckAmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Tournament)
admin.site.register(TournamentPlayer, TournamentPlayerAdmin)
admin.site.register(TopPlayer, TopPlayerAdmin)
admin.site.register(Round)
admin.site.register(Emparents)
