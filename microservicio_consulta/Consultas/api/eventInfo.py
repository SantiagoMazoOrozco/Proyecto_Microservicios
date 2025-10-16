import os
import sys
from datetime import datetime  # Importar datetime

# Agregar el directorio 'backend' al PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import requests
from dotenv import load_dotenv
from Consultas.api.location_mapping import get_department_by_city, get_zone_by_department

# Cargar la clave de la API desde el archivo .env
load_dotenv()

startgg_url = "https://api.start.gg/gql/alpha"
startgg_key = "204bdde1bb958e691497fa76febad15d"

if not startgg_key:
    raise ValueError('La clave de la API de Start.gg no está configurada. Verifica tu archivo .env')

def get_event_info(event_id):
    query = """
    query EventInfo($eventId: ID!) {
        event(id: $eventId) {
            id
            name
            startAt
            tournament {
                name
                slug
                city
                countryCode
            }
            standings(query: {perPage: 1}) {
                nodes {
                    placement
                    entrant {
                        name
                    }
                }
            }
        }
    }
    """
    variables = {'eventId': event_id}
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {startgg_key}'
    }

    try:
        response = requests.post(startgg_url, json={'query': query, 'variables': variables}, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Manejo robusto de errores y datos faltantes
        if 'errors' in data:
            print(f"Error en respuesta de start.gg: {data['errors']}")
            raise Exception('Error al obtener la información del evento desde start.gg')

        event = data.get('data', {}).get('event')
        if not event:
            print("No se encontró el evento con ese ID.")
            raise Exception('No se encontró el evento con ese ID.')

        tournament = event.get('tournament')
        if not tournament:
            print("No se encontró el torneo asociado al evento.")
            raise Exception('No se encontró el torneo asociado al evento.')

        tournament_slug = tournament.get('slug', '')
        tournament_url = f"https://www.start.gg/{tournament_slug}/event/{event['name'].replace(' ', '-').lower()}"

        # Consulta para obtener el número de asistentes
        attendees_query = """
        query AttendeeCount($tourneySlug: String!) {
          tournament(slug: $tourneySlug) {
            participants(query: {}) {
              pageInfo {
                total
              }
            }
          }
        }
        """
        attendees_variables = {'tourneySlug': tournament_slug}
        attendees_response = requests.post(startgg_url, json={'query': attendees_query, 'variables': attendees_variables}, headers=headers)
        attendees_response.raise_for_status()
        attendees_data = attendees_response.json()

        if 'errors' in attendees_data:
            print(f"Error en respuesta de asistentes: {attendees_data['errors']}")
            raise Exception('Error al obtener asistentes del torneo desde start.gg')

        attendees_count = attendees_data.get('data', {}).get('tournament', {}).get('participants', {}).get('pageInfo', {}).get('total', 'N/A')

        city = tournament.get('city', 'N/A')
        department = get_department_by_city(city)
        zone = get_zone_by_department(department)
        standings = event.get('standings', {}).get('nodes', [])
        winner_full_name = standings[0]['entrant']['name'] if standings else 'N/A'
        winner_name = winner_full_name.split('|')[-1].strip() if '|' in winner_full_name else winner_full_name

        start_date_unix = event.get('startAt')
        start_date = None
        if start_date_unix:
            from datetime import datetime
            start_date = datetime.utcfromtimestamp(start_date_unix).strftime('%Y-%m-%d')
        else:
            start_date = 'N/A'

        print(f"Nombre del torneo: {tournament.get('name', 'N/A')}")
        print(f"Asistentes: {attendees_count}")

        return {
            'name': event.get('name', 'N/A'),
            'tournament_name': tournament.get('name', 'N/A'),
            'attendees': attendees_count,
            'start_date': start_date,
            'city': city,
            'country': tournament.get('countryCode', 'N/A'),
            'department': department,
            'zone': zone,
            'winner': winner_name,
            'tournament_url': tournament_url
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching event info: {e}")
        raise Exception(f"Error fetching event info: {e}")
    except KeyError as e:
        print(f"KeyError: {e}")
        raise Exception(f"KeyError: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise Exception(f"Unexpected error: {e}")

def get_tournaments_by_country(country_code, per_page):
    query = """
    query TournamentsByCountry($cCode: String!, $perPage: Int!) {
        tournaments(query: {
            perPage: $perPage
            filter: {
                countryCode: $cCode
            }
        }) {
            nodes {
                id
                name
                countryCode
            }
        }
    }
    """
    variables = {'cCode': country_code, 'perPage': per_page}
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {startgg_key}'
    }

    try:
        response = requests.post(startgg_url, json={'query': query, 'variables': variables}, headers=headers)
        response.raise_for_status()
        data = response.json()

        if 'errors' in data:
            raise Exception(', '.join(error['message'] for error in data['errors']))

        tournaments = data['data']['tournaments']['nodes']
        return tournaments
    except requests.exceptions.RequestException as e:
        print(f"Error fetching tournaments by country: {e}")
        raise Exception(f"Error fetching tournaments by country: {e}")
    except KeyError as e:
        print(f"KeyError: {e}")
        raise Exception(f"KeyError: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise Exception(f"Unexpected error: {e}")

def get_tournament_location(event_id, coordinates, radius):
    query = """
    query TournamentLocation($eventId: ID!, $coordinates: String!, $radius: String!) {
        event(id: $eventId) {
            tournament {
                id
                name
                city
                location {
                    distanceFrom: $coordinates,
                    distance: $radius
                }
            }
        }
    }
    """
    variables = {
        'eventId': event_id,
        'coordinates': coordinates,
        'radius': radius
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {startgg_key}'
    }

    try:
        response = requests.post(startgg_url, json={'query': query, 'variables': variables}, headers=headers)
        response.raise_for_status()
        data = response.json()

        if 'errors' in data:
            raise Exception(', '.join(error['message'] for error in data['errors']))

        tournament = data['data']['event']['tournament']
        return {
            'id': tournament['id'],
            'name': tournament['name'],
            'city': tournament['city']
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching tournament location: {e}")
        raise Exception(f"Error fetching tournament location: {e}")
    except KeyError as e:
        print(f"KeyError: {e}")
        raise Exception(f"KeyError: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise Exception(f"Unexpected error: {e}")
