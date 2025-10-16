from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db import connection
from .models import Tournament
from .forms import TournamentForm
import logging

logger = logging.getLogger(__name__)

def get_tournaments(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                "Tournament_Name" AS tournament_name, 
                "Winner" AS winner, 
                "Attendees" AS attendees, 
                "Region" AS region, 
                "Pais" AS pais, 
                "Departamento" AS departamento, 
                "Ciudad" AS ciudad, 
                "Date" AS date, 
                "ID" AS id, 
                "URL" AS url,
                "Tier" AS tier
            FROM "Colombia Tournament"
            ORDER BY "Tournament_Name" ASC
            LIMIT 49999
            OFFSET 0;
        """)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
    tournaments = [dict(zip(columns, row)) for row in rows]
    return render(request, 'consultas/tournaments/view_colombia_tournament.html', {'tournaments': tournaments})

@csrf_exempt
def view_colombia_tournament(request):
    if request.method == 'GET':
        return get_tournaments(request)
    else:
        return HttpResponseBadRequest("Método no permitido")

@csrf_protect
def add_tournament(request):
    if request.method == 'POST':
        logger.debug("Solicitud POST recibida")
        form = TournamentForm(request.POST)
        if form.is_valid():
            tournament = form.save()
            logger.debug(f"Torneo guardado: {tournament}")
            return redirect('view_colombia_tournament')
        else:
            logger.error(f"Errores en el formulario: {form.errors}")
            return render(request, 'consultas/tournaments/create_tournament.html', {'form': form, 'errors': form.errors})
    logger.debug("Solicitud GET recibida")
    form = TournamentForm()
    return render(request, 'consultas/tournaments/create_tournament.html', {'form': form})

@csrf_protect
def edit_tournament(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    if request.method == 'POST':
        form = TournamentForm(request.POST, instance=tournament)
        if form.is_valid():
            form.save()
            return redirect('view_colombia_tournament')
    else:
        form = TournamentForm(instance=tournament)
    return render(request, 'consultas/tournaments/edit_tournament.html', {'form': form, 'tournament': tournament})

def enter_tournament_id(request):
    return render(request, 'consultas/tournaments/enter_tournament_id.html')

@csrf_protect
def delete_tournament(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    if request.method == 'POST':
        tournament.delete()
        return redirect('view_colombia_tournament')
    return render(request, 'consultas/tournaments/confirm_delete.html', {'tournament': tournament})

def enter_tournament_id_for_delete(request):
    return render(request, 'consultas/tournaments/enter_tournament_id_for_delete.html')
