import os
import pandas as pd
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest
from django.core.files.storage import FileSystemStorage
from django.db import connection, transaction
from .models import Player, Set
from .forms import UploadFileForm

def upload_excel(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            file_extension = os.path.splitext(file.name)[1].lower()
            if file_extension != '.xlsx':
                return HttpResponseBadRequest("Formato de archivo no soportado")
            try:
                df = pd.read_excel(file, engine='openpyxl')
                if df.empty:
                    return HttpResponseBadRequest("El archivo está vacío o no tiene columnas válidas")
                df.rename(columns={
                    'Nombre del Torneo': 'Tournament_Name',
                    'Ganador': 'Winner',
                    'Asistentes': 'Attendees',
                    'Region': 'Region',
                    'País': 'Pais',
                    'Departamento': 'Departamento',
                    'Ciudad': 'Ciudad',
                    'Fecha': 'Date',
                    'ID': 'ID',
                    'URL del Torneo': 'URL'
                }, inplace=True)
                if 'Date' in df.columns:
                    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                else:
                    return HttpResponseBadRequest("El archivo no contiene una columna 'Fecha' válida")
                if 'URL' not in df.columns:
                    df['URL'] = None
                if 'Tier' not in df.columns:
                    df['Tier'] = None
                with connection.cursor() as cursor:
                    for _, row in df.iterrows():
                        date_str = row['Date'].strftime('%Y-%m-%d') if not pd.isnull(row['Date']) else None
                        cursor.execute("""
                            INSERT INTO "Colombia Tournament" (
                                "Tournament_Name", "Winner", "Attendees", "Region", "Pais", "Departamento", "Ciudad", "Date", "ID", "URL", "Tier"
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT ("ID") DO NOTHING;
                        """, [
                            row['Tournament_Name'], row['Winner'], row['Attendees'], row['Region'], row['Pais'],
                            row['Departamento'], row['Ciudad'], date_str, row['ID'], row['URL'], row['Tier']
                        ])
                return redirect('view_colombia_tournament')
            except Exception as e:
                return HttpResponseBadRequest(f"Error al procesar el archivo: {e}")
    else:
        form = UploadFileForm()
    return render(request, 'consultas/upload_excel.html', {'form': form})

def upload_exceljugadores(request):
    """
    Procesa un XLSX con jugadores. Si faltan valores, los guarda como NULL.
    Se intenta primero usar get_player_details/_update_or_create_player; si no están,
    se hace un fallback con ORM creando registros con campos nullable.
    """
    # importar utilidades de getPlayerDetails de forma opcional
    try:
        from .api.getPlayerDetails import get_player_details, _update_or_create_player
    except Exception:
        get_player_details = None
        _update_or_create_player = None

    # intentar importar el modelo Player (opcional)
    try:
        from .models import Player as PlayerModel
    except Exception:
        PlayerModel = None

    summary = {"created": 0, "updated": 0, "skipped": 0, "errors": []}

    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        fs = FileSystemStorage()
        filename = fs.save(excel_file.name, excel_file)
        file_path = fs.path(filename)
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
        except Exception as e:
            return render(request, 'consultas/upload_exceljugadores.html', {"error": f"Error leyendo Excel: {e}"})

        # Normalizar columnas esperadas
        required_columns = [
            "ID", "GamerTag", "Slug", "Prefijo", "Nombre", "Pais", "Departamento", "Region", "Ciudad",
            "Twitter", "Discord", "Twitch"
        ]
        for col in required_columns:
            if col not in df.columns:
                df[col] = ''

        # convertir NaN a '' y luego a None cuando sea vacío
        df = df.fillna('')

        # procesar filas
        for _, row in df.iterrows():
            player_id_raw = row.get('ID') or None
            # normalizar player_id numérico si es posible
            player_id = None
            try:
                if player_id_raw not in (None, '', 'N/A'):
                    player_id = int(player_id_raw)
            except Exception:
                player_id = None

            gamerTag = (row.get('GamerTag') or row.get('Gamertag') or '').strip() or None

            # Priorizar obtener datos desde start.gg si hay ID y la utilidad está disponible
            details = None
            if player_id and get_player_details:
                try:
                    details = get_player_details(int(player_id))
                    if isinstance(details, dict) and details.get('error'):
                        details = None
                except Exception as e:
                    summary['errors'].append({"row_id": player_id, "error": f"Error fetching from upstream: {e}"})
                    details = None

            if not details:
                # construir details mínimos desde el Excel (None para valores vacíos)
                def norm(v):
                    if v in (None, '', 'N/A'):
                        return None
                    return v
                details = {
                    "ID": player_id,
                    "GamerTag": norm(gamerTag),
                    "Slug": norm(row.get('Slug')),
                    "Prefijo": norm(row.get('Prefijo')),
                    "Nombre": norm(row.get('Nombre')),
                    "Pais": norm(row.get('Pais')),
                    "Departamento": norm(row.get('Departamento')),
                    "Region": norm(row.get('Region')),
                    "Ciudad": norm(row.get('Ciudad')),
                    "Twitter": norm(row.get('Twitter')),
                    "Discord": norm(row.get('Discord')),
                    "Twitch": norm(row.get('Twitch')),
                }

            # intentar persistir: primero la utilidad especializada si existe
            persisted = False
            if _update_or_create_player and PlayerModel:
                try:
                    with transaction.atomic():
                        created, obj = _update_or_create_player(PlayerModel, details)
                        if created:
                            summary['created'] += 1
                        else:
                            summary['updated'] += 1
                        persisted = True
                except Exception as e:
                    summary['errors'].append({"player_id": details.get('ID'), "error": str(e)})
                    persisted = False

            # fallback al ORM simple si hay modelo y no se persisitó arriba
            if not persisted and PlayerModel:
                try:
                    with transaction.atomic():
                        # buscar por PK(ID) o gamertag (case-insensitive)
                        obj = None
                        if details.get('ID') is not None:
                            try:
                                obj = PlayerModel.objects.filter(pk=details.get('ID')).first()
                            except Exception:
                                obj = None
                        if obj is None and details.get('GamerTag'):
                            try:
                                # intentar ambas variantes de campo
                                if 'gamertag' in [f.name for f in PlayerModel._meta.get_fields()]:
                                    obj = PlayerModel.objects.filter(gamertag__iexact=details.get('GamerTag')).first()
                                elif 'GamerTag' in [f.name for f in PlayerModel._meta.get_fields()]:
                                    obj = PlayerModel.objects.filter(GamerTag__iexact=details.get('GamerTag')).first()
                            except Exception:
                                obj = None

                        created_flag = False
                        if obj is None:
                            # crear nueva instancia; si details.ID existe, asignarlo
                            if details.get('ID') is not None:
                                obj = PlayerModel(id=details.get('ID'))
                            else:
                                obj = PlayerModel()
                            created_flag = True

                        # asignar atributos si existen, usando None para vacíos
                        mapping = {
                            'ID': 'id',
                            'GamerTag': 'gamertag',
                            'Slug': 'slug',
                            'Prefijo': 'prefijo',
                            'Nombre': 'nombre',
                            'Pais': 'pais',
                            'Departamento': 'departamento',
                            'Region': 'region',
                            'Ciudad': 'ciudad',
                            'Twitter': 'twitter',
                            'Discord': 'discord',
                            'Twitch': 'twitch'
                        }
                        for k, v in details.items():
                            attr = mapping.get(k)
                            if not attr:
                                continue
                            try:
                                # solo asignar si el atributo existe en el modelo
                                if hasattr(obj, attr):
                                    setattr(obj, attr, v)
                            except Exception:
                                # ignorar errores de asignación
                                pass

                        obj.save()
                        if created_flag:
                            summary['created'] += 1
                        else:
                            summary['updated'] += 1
                        persisted = True
                except Exception as e:
                    summary['errors'].append({"player_id": details.get('ID'), "error": str(e)})
                    persisted = False

            if not persisted:
                summary['skipped'] += 1

        # eliminar archivo subido temporalmente
        try:
            os.remove(file_path)
        except Exception:
            pass

        # render con resumen para inspección
        return render(request, 'consultas/upload_exceljugadores.html', {"summary": summary})

    # GET: mostrar formulario
    return render(request, 'consultas/upload_exceljugadores.html')

def upload_excelsets(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            file_extension = os.path.splitext(file.name)[1].lower()
            if file_extension != '.xlsx':
                return HttpResponseBadRequest("Formato de archivo no soportado")
            try:
                df = pd.read_excel(file, engine='openpyxl')
                if df.empty:
                    return HttpResponseBadRequest("El archivo está vacío o no tiene columnas válidas")
                df.rename(columns={
                    'ID Torneo': 'id_torneo',
                    'ID Set': 'id_set',
                    'ID Jugador 1': 'id_player_1',
                    'Jugador 1': 'player_1',
                    'Puntuación Jugador 1': 'player_1_score',
                    'ID Jugador 2': 'id_player_2',
                    'Jugador 2': 'player_2',
                    'Puntuación Jugador 2': 'player_2_score',
                    'Phase': 'phase',
                    'Event Name': 'event_name',
                    'Tournament Name': 'tournament_name',
                    'Player 1 Characters': 'player_1_characters',
                    'Player 2 Characters': 'player_2_characters'
                }, inplace=True)
                df = df.dropna(subset=['player_1_score', 'player_2_score'])
                df = df.reset_index(drop=True)
                # Asignación heurística de ronda si no existe columna 'Ronda'
                if 'Ronda' in df.columns:
                    ronda_col = df['Ronda']
                else:
                    rounds = [
                        'Grand Final', 'Winners Final', 'Losers Final', 'Winners Semifinal', 'Losers Semifinal',
                        'Winners Quarterfinal', 'Losers Quarterfinal'
                    ]
                    n = len(df)
                    ronda_col = ['Bracket'] * n
                    for i, round_name in enumerate(rounds):
                        if n - 1 - i >= 0:
                            ronda_col[n - 1 - i] = round_name
                with connection.cursor() as cursor:
                    for idx, row in df.iterrows():
                        ronda = ronda_col[idx] if ronda_col is not None else None
                        try:
                            cursor.execute("""
                                INSERT INTO "Colombia_Sets" (
                                    "id_torneo", "id_set", "id_player_1", "player_1", "player_1_score",
                                    "id_player_2", "player_2", "player_2_score", "phase", "event_name",
                                    "tournament_name", "player_1_characters", "player_2_characters", "ronda"
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, [
                                row.get('id_torneo'),
                                row.get('id_set'),
                                row.get('id_player_1'),
                                row.get('player_1'),
                                row.get('player_1_score'),
                                row.get('id_player_2'),
                                row.get('player_2'),
                                row.get('player_2_score'),
                                row.get('phase'),
                                row.get('event_name'),
                                row.get('tournament_name'),
                                row.get('player_1_characters', ''),
                                row.get('player_2_characters', ''),
                                ronda
                            ])
                        except Exception:
                            continue
                return redirect('view_all_sets')
            except Exception as e:
                return HttpResponseBadRequest(f"Error al procesar el archivo: {e}")
        else:
            return HttpResponseBadRequest("Formulario no válido")
    else:
        form = UploadFileForm()
    return render(request, 'consultas/upload_excel_sets_colombia.html', {'form': form})
