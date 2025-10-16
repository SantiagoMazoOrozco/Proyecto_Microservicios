import requests
import time
from dotenv import load_dotenv
load_dotenv()

startgg_url = "https://api.start.gg/gql/alpha"
# usar el token nuevo y nombre consistente
startgg_key = "3e417c2b55e54203247b7501c15e70ca"

def delay(seconds):
    time.sleep(seconds)

def get_event_results(event_id):
    num_entrants = 0
    num_entrants_found = 0
    page_number = 1
    results = []

    try:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {startgg_key}"
        }

        # Primera solicitud para obtener el número total de participantes
        response = requests.post(startgg_url, json={
            "query": """
            query EventSets($eventId: ID!, $page: Int!, $perPage: Int!) { 
                event(id: $eventId) {
                    sets(page: $page, perPage: $perPage, sortType: STANDARD) {
                        pageInfo { total }
                        nodes { id slots { entrant { name } } }
                    }
                }
            }
            """,
            "variables": {
                "eventId": event_id,
                "page": 1,
                "perPage": 1
            }
        }, headers=headers)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print("Respuesta de la API (get_event_results - EventSets):", response.status_code, response.text)
            raise e

        data = response.json()
        if data.get('data') and data['data'].get('event') and data['data']['event'].get('sets') and data['data']['event']['sets'].get('pageInfo'):
            num_entrants = data['data']['event']['sets']['pageInfo']['total']
        else:
            raise Exception('Datos de respuesta no esperados para EventSets')

        delay(1)

        while num_entrants_found < num_entrants:
            response = requests.post(startgg_url, json={
                "query": """
                query EventStandings($eventId: ID!, $page: Int!, $perPage: Int!) { 
                    event(id: $eventId) {
                        standings(query: { perPage: $perPage, page: $page }) {
                            nodes {
                                placement
                                entrant { name }
                            }
                        }
                    }
                }
                """,
                "variables": {
                    "eventId": event_id,
                    "page": page_number,
                    "perPage": 50
                }
            }, headers=headers)

            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                print("Respuesta de la API (get_event_results - Standings):", response.status_code, response.text)
                raise e

            data = response.json()
            # Corrección: quitar paréntesis extra que provocaba SyntaxError
            if data.get('data') and data['data'].get('event') and data['data']['event'].get('standings') and data['data']['event']['standings'].get('nodes'):
                nodes = data['data']['event']['standings']['nodes']
                if not nodes:
                    break
                for node in nodes:
                    entrant = node.get('entrant') or {}
                    results.append({
                        'name': entrant.get('name'),
                        'placement': node.get('placement')
                    })
                num_entrants_found += len(nodes)
            else:
                raise Exception('Datos de respuesta no esperados para EventStandings')

            page_number += 1
            delay(1)
    except Exception as e:
        print('Error al obtener las posiciones del evento:', e)
        results = {"error": str(e)}

    return results
