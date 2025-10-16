import os
import requests
from dotenv import load_dotenv
import traceback
from django.http import JsonResponse
from .location_mapping import get_department_by_city, get_region_by_department, get_zone_by_department
from datetime import datetime

# intentar importar utilidades de player (si el módulo está disponible)
try:
    from .getPlayerDetails import get_player_details, _update_or_create_player, LocalPlayerModel as PlayersModuleLocalModel
except Exception:
    # si falla la importación, las operaciones de creación se saltarán
    get_player_details = None
    _update_or_create_player = None
    PlayersModuleLocalModel = None

# Cargar la clave de la API desde el archivo .env
load_dotenv()

startgg_url = "https://api.start.gg/gql/alpha"
startgg_key = "3e417c2b55e54203247b7501c15e70ca"

if not startgg_key:
    raise ValueError('La clave de la API de Start.gg no está configurada. Verifica tu archivo .env')

def get_tournament_details(tournament_id, attendees_per_page=100):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {startgg_key}'
    }
    
    query = """
    query TournamentQuery($id: ID!, $perPage: Int!, $page: Int!) {
        tournament(id: $id) {
            name
            city
            countryCode
            startAt
            slug
            events {
                standings(query: { perPage: 1, page: 1 }) {
                    nodes {
                        entrant {
                            name
                        }
                    }
                }
            }
            numAttendees
            participants(query: {perPage: $perPage, page: $page}) {
                pageInfo {
                    totalPages
                }
                nodes {
                    id
                    gamerTag
                    player {
                        id
                    }
                }
            }
        }
    }
    """
    
    variables = {
        'id': tournament_id,
        'perPage': attendees_per_page,
        'page': 1
    }
    try:
        response = requests.post(
            startgg_url,
            headers=headers,
            json={'query': query, 'variables': variables},
            timeout=30
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            print("Respuesta de la API (get_tournament_details page 1):", response.status_code)
            print(response.text)
            body_text = response.text
            try:
                body_json = response.json()
            except Exception:
                body_json = None
            return {"success": False, "error": "Upstream API HTTP error", "status_code": response.status_code, "details": body_json or body_text}
 
        try:
            data = response.json()
        except Exception as ex:
            print("No se pudo parsear JSON de la respuesta (get_tournament_details):", ex)
            print("Respuesta raw:", response.text)
            return {"success": False, "error": "Invalid JSON from upstream", "details": response.text}
 
        if 'errors' in data:
            print("Errors en respuesta upstream (get_tournament_details):", data['errors'])
            return {"success": False, "error": "Upstream returned GraphQL errors", "details": data.get('errors') or data}
 
        if 'data' not in data or 'tournament' not in data['data'] or data['data']['tournament'] is None:
            print("Respuesta inesperada (get_tournament_details):", data)
            return {"success": False, "error": "Invalid API response structure", "details": data}
 
        tournament = data['data']['tournament']
        participants = tournament.get('participants', {})
        attendees = [
            {
                "participant_id": p.get("id"),
                "player_id": p.get("player", {}).get("id"),
                "gamerTag": p.get("gamerTag")
            }
            for p in participants.get('nodes', [])
        ]
        total_pages = participants.get('pageInfo', {}).get('totalPages', 1)
        for page in range(2, total_pages + 1):
            variables['page'] = page
            resp = requests.post(
                startgg_url,
                headers=headers,
                json={'query': query, 'variables': variables},
                timeout=30
            )
            try:
                resp.raise_for_status()
            except requests.exceptions.HTTPError:
                print(f"Respuesta de la API (get_tournament_details page {page}):", resp.status_code)
                print(resp.text)
                try:
                    body_json = resp.json()
                except Exception:
                    body_json = resp.text
                return {"success": False, "error": f"Upstream HTTP error page {page}", "status_code": resp.status_code, "details": body_json}
            try:
                d = resp.json()
            except Exception as ex:
                print(f"No se pudo parsear JSON en page {page}:", ex)
                print("Respuesta raw:", resp.text)
                return {"success": False, "error": f"Invalid JSON on page {page}", "details": resp.text}
            if 'errors' in d:
                print(f"GraphQL errors on page {page}:", d['errors'])
                return {"success": False, "error": f"GraphQL errors on page {page}", "details": d.get('errors') or d}
            if 'data' not in d or 'tournament' not in d['data'] or d['data']['tournament'] is None:
                print(f"Respuesta inesperada page {page}:", d)
                return {"success": False, "error": f"Invalid API response structure on page {page}", "details": d}
            more_participants = d['data']['tournament'].get('participants', {}).get('nodes', [])
            attendees += [
                {
                    "participant_id": p.get("id"),
                    "player_id": p.get("player", {}).get("id"),
                    "gamerTag": p.get("gamerTag")
                }
                for p in more_participants
            ]
        winner = 'N/A'
        events = tournament.get('events', [])
        if events and isinstance(events, list):
            standings = events[0].get('standings', {}).get('nodes', [])
            if standings and isinstance(standings, list) and len(standings) > 0:
                entrant = standings[0].get('entrant', {})
                winner = entrant.get('name', 'N/A')
        city = tournament.get('city') or None
        country_code = tournament.get('countryCode') or None
        department = get_department_by_city(city) if city else None
        region = get_region_by_department(department) if department else None

        start_date = None
        if tournament.get('startAt'):
            try:
                ts = int(tournament.get('startAt'))
                if ts > 10**12:
                    ts = ts / 1000
                start_date = datetime.utcfromtimestamp(int(ts)).strftime('%Y-%m-%d')
            except Exception:
                start_date = None

        details = {
            'name': tournament.get('name', 'N/A'),
            'winner': winner,
            'numAttendees': tournament.get('numAttendees', 'N/A'),
            'attendees': attendees,
            'city': city,
            'country_code': country_code,
            'department': department,
            'region': region,
            'start_date': start_date,
            'slug': tournament.get('slug')
        }
        return {"success": True, "details": details}
    except requests.exceptions.RequestException as e:
        print('Error al obtener los detalles del torneo:', e)
        traceback.print_exc()
        return {"success": False, "error": "RequestException", "details": str(e)}
    except Exception as e:
        print('Error inesperado en get_tournament_details:', e)
        traceback.print_exc()
        return {"success": False, "error": "Unexpected error", "details": str(e)}

def get_event_info_view(request):
    """
    API view que acepta event_id (GET, POST form-data o POST JSON).
    Retorna los detalles del torneo asociado al evento en un formato plano que consuma el frontend.
    Acepta opcionalmente create_players=1 para intentar crear/actualizar jugadores faltantes en la BD.
    """
    event_id = request.GET.get('event_id') or request.GET.get('id')
    # aceptar flag para auto-crear jugadores faltantes
    create_players_flag = request.GET.get('create_players') or request.POST.get('create_players')
    if request.method == 'POST' and not event_id:
        event_id = request.POST.get('event_id') or request.POST.get('id')
    if request.method == 'POST' and not event_id and request.content_type and 'application/json' in request.content_type:
        try:
            import json
            body = json.loads(request.body.decode('utf-8') or "{}")
            event_id = event_id or body.get('event_id') or body.get('id')
            if create_players_flag is None:
                create_players_flag = body.get('create_players')
        except Exception:
            pass

    # normalizar flag a boolean
    create_players = False
    if create_players_flag is not None:
        create_players = str(create_players_flag).lower() in ['1', 'true', 'yes']

    if not event_id:
        return JsonResponse({"success": False, "error": "Missing parameter: event_id"}, status=400)

    try:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {startgg_key}'
        }
        query = """
        query EventToTournament($eventId: ID!) {
            event(id: $eventId) {
                id
                name
                tournament {
                    id
                    name
                }
            }
        }
        """
        variables = {'eventId': int(event_id)}
        resp = requests.post(startgg_url, headers=headers, json={'query': query, 'variables': variables}, timeout=30)
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            print("Respuesta de la API (EventToTournament):", resp.status_code)
            print(resp.text)
            return JsonResponse({"success": False, "error": "Upstream API HTTP error", "status_code": resp.status_code, "body": resp.text}, status=502)

        data = resp.json()
        if 'errors' in data or 'data' not in data or data['data'].get('event') is None:
            print("Respuesta inesperada (EventToTournament):", data)
            return JsonResponse({"success": False, "error": "Invalid upstream response", "body": data}, status=502)

        tournament = data['data']['event'].get('tournament')
        if not tournament or not tournament.get('id'):
            return JsonResponse({"success": False, "error": "Tournament not found for event"}, status=404)

        tournament_id = tournament['id']
        result = get_tournament_details(tournament_id)

        if isinstance(result, dict) and result.get('success') is True:
            details = result['details']
            attendees = details.get('attendees', []) or []
            # si el cliente pidió crear jugadores faltantes, intentarlo
            player_sync_summary = None
            if create_players:
                summary = {"created": 0, "updated": 0, "skipped": 0, "errors": []}
                # sólo si las utilidades están disponibles y hay un modelo
                if get_player_details is None or _update_or_create_player is None:
                    summary['errors'].append("Player creation utilities not available on server")
                else:
                    # intentar obtener modelo desde el módulo getPlayerDetails si está expuesto
                    target_model = PlayersModuleLocalModel if PlayersModuleLocalModel is not None else None
                    # fallback: intentar importar desde Consultas.models
                    if target_model is None:
                        try:
                            from Consultas.models import Player as TargetPlayerModel
                            target_model = TargetPlayerModel
                        except Exception:
                            target_model = None

                    # Verificar que la tabla del modelo exista antes de iterar (evita "no such table")
                    if target_model is not None:
                        try:
                            from django.db import connection
                            if target_model._meta.db_table not in connection.introspection.table_names():
                                summary['errors'].append(f"Player table not found in DB: '{target_model._meta.db_table}'. Run migrations.")
                                # anular target_model para que el bucle no intente crear
                                target_model = None
                        except Exception as e:
                            summary['errors'].append(f"Unable to inspect DB tables: {e}")
                            target_model = None

                    for a in attendees:
                        p_id = a.get('player_id')
                        if not p_id:
                            summary['skipped'] += 1
                            continue
                        try:
                            # obtener detalles desde start.gg
                            p_details = get_player_details(int(p_id))
                            if isinstance(p_details, dict) and p_details.get('error'):
                                summary['errors'].append({"player_id": p_id, "error": p_details.get('error')})
                                continue
                            if target_model is None:
                                # no hay modelo para persistir
                                summary['skipped'] += 1
                                continue
                            # crear/actualizar en BD
                            try:
                                created, obj = _update_or_create_player(target_model, p_details)
                                if created:
                                    summary['created'] += 1
                                else:
                                    summary['updated'] += 1
                            except Exception as e:
                                summary['errors'].append({"player_id": p_id, "error": str(e)})
                        except Exception as e:
                            summary['errors'].append({"player_id": p_id, "error": str(e)})
                player_sync_summary = summary

            response_data = {
                "success": True,
                "tournament_name": details.get('name'),
                "winner": details.get('winner'),
                "attendees": details.get('numAttendees'),
                "attendees_list": details.get('attendees', []),
                "tournament_id": tournament_id,
                "tournament_url": f"https://start.gg/tournament/{tournament_id}",
                "region": details.get('region', None),
                "country": details.get('country_code', 'CO'),
                "department": details.get('department', None),
                "city": details.get('city', None),
                "start_date": details.get('start_date', None)
            }
            if player_sync_summary is not None:
                response_data['player_sync_summary'] = player_sync_summary
            return JsonResponse(response_data, status=200)
        error_details = result.get('details') if result.get('details') is not None else result.get('body') if isinstance(result, dict) else None
        return JsonResponse({"success": False, "error": result.get('error', 'Unknown error'), "details": error_details}, status=502)
    except requests.exceptions.RequestException as e:
        print("RequestException in get_event_info_view:", str(e))
        traceback.print_exc()
        return JsonResponse({"success": False, "error": "Request error contacting upstream API", "details": str(e)}, status=502)
    except Exception as e:
        print("Unexpected exception in get_event_info_view:", str(e))
        traceback.print_exc()
        return JsonResponse({"success": False, "error": "Internal server error", "details": str(e)}, status=500)

if __name__ == "__main__":
    tournament_id = "1154661"
    result = get_tournament_details(tournament_id)
    print(result)