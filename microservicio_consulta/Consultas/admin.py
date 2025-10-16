from django.contrib import admin
from .models import (
    Character, CharacterSkin, Tournament, Player, TournamentParticipant,
    Event, Set
    # MatchCharacter  # <-- Elimina o comenta esta línea si MatchCharacter no existe o no está definido
)

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'gamertag', 'nombre', 'pais', 'ciudad', 'main_character')
    search_fields = ('gamertag', 'nombre', 'pais', 'ciudad')

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('tournament_name', 'date', 'ciudad', 'tier')  # Cambia 'city' por 'ciudad'
    search_fields = ('tournament_name',)
    list_filter = ('date', 'tier', 'ciudad')  # Cambia 'city' por 'ciudad'

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'phase', 'tournament')
    list_filter = ('phase',)

@admin.register(Set)
class SetAdmin(admin.ModelAdmin):
    list_display = [
        'id_torneo',
        'id_set',
        'id_player_1',
        'player_1',
        'player_1_score',
        'id_player_2',
        'player_2',
        'player_2_score',
        'phase',
        'event_name',
        'tournament_name',
        'player_1_characters',
        'player_2_characters',
    ]
    list_filter = [
        'phase',
        'event_name',
        'tournament_name',
    ]

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'game')
    search_fields = ('name',)

@admin.register(TournamentParticipant)
class TournamentParticipantAdmin(admin.ModelAdmin):
    list_display = ('gamertag', 'player', 'tournament', 'participant_id')
    list_filter = ('tournament',)
    search_fields = ('gamertag', 'player__nickname')
