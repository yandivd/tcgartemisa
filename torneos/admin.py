from django.contrib import admin
from .models import *
from django.utils.html import format_html
# Register your models here.
class PlayerAdmin(admin.ModelAdmin):
    list_display=['user','victorys', 'defeats', 'ptos']

class TournamentPlayerAdmin(admin.ModelAdmin):
    list_display=['jugador', 'victorys', 'defeats', 'draws','byes', 'ptos','OMW', 'PGW', 'OGW']

    def deck_image(self, obj):
        if obj.deck and obj.deck.img:  # Verifica si el Deck tiene una imagen asociada
            return format_html(f'<img src="{obj.deck.img.url}" width="50" height="50" style="object-fit: cover;" />')
        return "No hay imagen"
    deck_image.short_description = "Imagen del Deck"

class TopPlayerAdmin(admin.ModelAdmin):
    list_display=['tournament_player','position']

class DeckAdmin(admin.ModelAdmin):
    list_display = ['name', 'imagen_tag']  # Asegúrate de incluir 'imagen_tag' en list_display

    def imagen_tag(self, obj):
        if obj.img:  # Cambia 'imagen' a 'img'
            return format_html(f'<img src="{obj.img.url}" width="50" height="50" style="object-fit: cover;" />')
        return "No hay imagen"
    imagen_tag.short_description = 'Imagen'


admin.site.register(Deck, DeckAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Tournament)
admin.site.register(TournamentPlayer, TournamentPlayerAdmin)
admin.site.register(TopPlayer, TopPlayerAdmin)
admin.site.register(Round)
admin.site.register(Emparents)
