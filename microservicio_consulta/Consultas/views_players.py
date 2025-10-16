from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from .models import Player
from .forms import PlayerForm
import logging

logger = logging.getLogger(__name__)

def view_all_players(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                "ID", 
                "Gamertag", 
                "Slug", 
                "Prefijo", 
                "Nombre", 
                "Pais", 
                "Departamento", 
                "Region", 
                "Ciudad", 
                "Twitter", 
                "Discord", 
                "Twitch"
            FROM "main"."Colombia_Players"
            ORDER BY "ID" ASC
            LIMIT 49999
            OFFSET 0;
        """)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
    players = [dict(zip(columns, row)) for row in rows]
    return render(request, 'consultas/players/view_all_players.html', {'players': players})

def player_create(request):
    logger.debug("Solicitud POST recibida para crear jugador" if request.method == 'POST' else "Solicitud GET recibida para crear jugador")
    if request.method == 'POST':
        form = PlayerForm(request.POST)
        if form.is_valid():
            player = form.save()
            logger.debug(f"Jugador guardado: {player}")
            return redirect('view_all_players')
        else:
            logger.error(f"Errores en el formulario: {form.errors}")
            return render(request, 'consultas/players/create_player.html', {'form': form, 'errors': form.errors})
    form = PlayerForm()
    return render(request, 'consultas/players/create_player.html', {'form': form})

def edit_player(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    if request.method == 'POST':
        player.first_name = request.POST['first_name']
        player.last_name = request.POST['last_name']
        player.nickname = request.POST['nickname']
        player.country = request.POST['country']
        player.zone = request.POST['zone']
        player.city = request.POST['city']
        player.team = request.POST['team']
        player.team_secondary = request.POST['team_secondary']
        player.play_offline = request.POST.get('play_offline') == 'on'
        player.play_online = request.POST.get('play_online') == 'on'
        player.main_character = request.POST['main_character']
        player.second_option_player = request.POST['second_option_player']
        player.third_option_player = request.POST['third_option_player']
        player.twitter = request.POST['twitter']
        player.instagram = request.POST['instagram']
        player.tiktok = request.POST['tiktok']
        player.user_startgg = request.POST['user_startgg']
        player.code_startgg = request.POST['code_startgg']
        player.url_startgg = request.POST['url_startgg']
        player.url_smashdata = request.POST['url_smashdata']
        player.combined_teams = request.POST['combined_teams']
        player.combined_characters = request.POST['combined_characters']
        player.logo_team_1 = request.POST['logo_team_1']
        player.logo_team_2 = request.POST['logo_team_2']
        player.logo_main = request.POST['logo_main']
        player.logo_2 = request.POST['logo_2']
        player.logo_3 = request.POST['logo_3']
        player.save()
        return redirect('view_all_players')
    return render(request, 'consultas/players/edit_player.html', {'player': player})

def enter_player_id(request):
    return render(request, 'consultas/players/enter_player_id.html')

def delete_player(request, player_id):
    # Elimina directamente de la tabla Colombia_Players usando SQL
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM "main"."Colombia_Players" WHERE "ID" = %s', [player_id])
        return redirect('view_all_players')
    # Obtener datos del jugador para mostrar en la confirmación
    with connection.cursor() as cursor:
        cursor.execute('SELECT "ID", "Nombre" FROM "main"."Colombia_Players" WHERE "ID" = %s', [player_id])
        row = cursor.fetchone()
        player = {'ID': row[0], 'Nombre': row[1]} if row else {'ID': player_id, 'Nombre': ''}
    return render(request, 'consultas/players/confirm_delete.html', {'player': player})
