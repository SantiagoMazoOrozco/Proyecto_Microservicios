from django.urls import path
from .api.getEventId import get_event_id_view
from .api.getTournamentDetails import get_event_info_view
from .api.getPlayerDetails import get_player_info_view, sync_players_from_tournament_view, ensure_player_view
from .api.get_set_info import get_set_info
from .api.setByTournament import get_sets_by_event
from .api.eventInfo import get_tournaments_by_country
from . import views

urlpatterns = [
    path('health/', views.api_health, name='api_health'),
    path('get-event-id/', get_event_id_view, name='api_get_event_id'),
    path('get-event-info/', get_event_info_view, name='api_get_event_info'),
    path('get-event-results/', views.get_event_results, name='api_get_event_results'),
    path('get-player-info/', get_player_info_view, name='api_get_player_info'),
    path('sync-players/', sync_players_from_tournament_view, name='api_sync_players'),
    path('ensure-player/', ensure_player_view, name='api_ensure_player'),
    path('get-sets-by-tournament/', views.get_sets_by_tournament_view, name='api_get_sets_by_tournament'),
    path('get-set-info/', views.get_set_info_api, name='api_get_set_info'),
    path('get-tournaments-by-country/', views.get_tournaments_by_country_view, name='api_get_tournaments_by_country'),
    path('autocomplete-players/', views.autocomplete_players, name='api_autocomplete_players'),
]
