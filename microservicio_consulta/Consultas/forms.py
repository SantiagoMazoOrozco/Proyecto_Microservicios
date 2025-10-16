from django import forms
from .models import Set, Player, Tournament

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = [
            'id', 'gamertag', 'slug', 'prefijo', 'nombre', 'pais', 'departamento', 'region', 'ciudad',
            'twitter', 'discord', 'twitch', 'main_character', 'secundary_character'
        ]

class UploadFileForm(forms.Form):
    file = forms.FileField()

class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = [
            'id', 'tournament_name', 'winner', 'attendees', 'region', 'pais', 
            'departamento', 'ciudad', 'date', 'url', 'tier'
        ]

class SetForm(forms.ModelForm):
    class Meta:
        model = Set
        fields = [
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