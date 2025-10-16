import os
import requests
from dotenv import load_dotenv
import time

# Cargar la clave de la API desde el archivo .env
load_dotenv()

startgg_url = "https://api.start.gg/gql/alpha"
startgg_key = "3e417c2b55e54203247b7501c15e70ca"

if not startgg_key:
    raise ValueError('La clave de la API de Start.gg no está configurada. Verifica tu archivo .env')

def delay(seconds):
    time.sleep(seconds)

def get_entrant_to_player_id_by_tournament(tournament_id):
    entrant_to_player = {}
    page = 1
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {startgg_key}'}
    while True:
        query_participants = """
        query TournamentParticipants($id: ID!, $perPage: Int!, $page: Int!) {
            tournament(id: $id) {
                participants(query: {perPage: $perPage, page: $page}) {
                    pageInfo { totalPages }
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
        variables_participants = {'id': tournament_id, 'perPage': 100, 'page': page}
        try:
            resp = requests.post(
                startgg_url,
                headers=headers,
                json={'query': query_participants, 'variables': variables_participants}
            )
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"Error API TournamentParticipants (page {page}):", resp.status_code, resp.text)
            break
        except Exception as e:
            print(f"Request error TournamentParticipants (page {page}): {e}")
            break

        d = resp.json()
        tournament = d.get('data', {}).get('tournament', {})
        participants = tournament.get('participants', {})
        for p in participants.get('nodes', []):
            player_id = p.get("player", {}).get("id") if p.get("player") else None
            entrant_to_player[str(p.get("id"))] = player_id
        if page >= participants.get('pageInfo', {}).get('totalPages', 0):
            break
        page += 1
        delay(0.25)
    return entrant_to_player

def get_player_id_from_entrant_id(entrant_id):
    query = """
    query EntrantQuery($id: ID!) {
        entrant(id: $id) {
            id
            participants {
                player {
                    id
                }
            }
        }
    }
    """
    variables = {"id": int(entrant_id)}
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {startgg_key}'}
    try:
        response = requests.post(
            startgg_url,
            headers=headers,
            json={'query': query, 'variables': variables}
        )
        response.raise_for_status()
        data = response.json()
        entrant = data.get('data', {}).get('entrant', {})
        participants = entrant.get('participants', [])
        if participants and participants[0].get('player') and participants[0]['player'].get('id'):
            return participants[0]['player']['id']
    except requests.exceptions.HTTPError as e:
        print(f"Error API EntrantQuery for entrant_id {entrant_id}:", response.status_code, response.text)
    except Exception as e:
        print(f"Error obteniendo player_id para entrant_id {entrant_id}: {e}")
    return None

def get_phase_name_from_phase_id(phase_id):
    query = """
    query PhaseName($phaseId: ID!) {
      phase(id: $phaseId) {
        id
        name
      }
    }
    """
    variables = {"phaseId": int(phase_id)}
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {startgg_key}'}
    try:
        response = requests.post(
            startgg_url,
            headers=headers,
            json={'query': query, 'variables': variables}
        )
        response.raise_for_status()
        data = response.json()
        phase = data.get('data', {}).get('phase', {})
        return phase.get('name')
    except requests.exceptions.HTTPError as e:
        print(f"Error API PhaseName for phase_id {phase_id}:", response.status_code, response.text)
    except Exception as e:
        print(f"Error obteniendo nombre de fase para phase_id {phase_id}: {e}")
        return None

def get_sets_by_event(event_id):
    sets = []
    page_number = 1
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {startgg_key}'}

    query_event = """
    query EventQuery($eventId: ID!) {
        event(id: $eventId) {
            tournament {
                id
            }
        }
    }
    """
    variables_event = {'eventId': event_id}
    try:
        response_event = requests.post(
            startgg_url,
            headers=headers,
            json={'query': query_event, 'variables': variables_event}
        )
        response_event.raise_for_status()
        data_event = response_event.json()
        tournament = data_event.get('data', {}).get('event', {}).get('tournament', {})
        tournament_id = tournament.get('id')
    except requests.exceptions.HTTPError as e:
        print(f"Error API EventQuery for event_id {event_id}:", response_event.status_code, response_event.text)
        return sets
    except Exception as e:
        print(f"Error obteniendo torneo para event_id {event_id}: {e}")
        return sets

    try:
        entrant_to_player_id = get_entrant_to_player_id_by_tournament(tournament_id)
    except Exception as e:
        entrant_to_player_id = {}

    def process_nodes(nodes):
        for node in nodes:
            display_score = node.get('displayScore', 'N/A')
            player1, player2 = display_score.split(' - ') if ' - ' in display_score else (display_score, '')
            player1_name, player1_score = player1.rsplit(' ', 1) if ' ' in player1 else (player1, '')
            player2_name, player2_score = player2.rsplit(' ', 1) if ' ' in player2 else (player2, '')

            player1_name = player1_name.split('|')[-1].strip()
            player2_name = player2_name.split('|')[-1].strip()

            player1_participant_id = str(node['slots'][0]['entrant']['id']) if node['slots'][0]['entrant'] else None
            player2_participant_id = str(node['slots'][1]['entrant']['id']) if node['slots'][1]['entrant'] else None

            player1_id = get_player_id_from_entrant_id(player1_participant_id) if player1_participant_id else None
            player2_id = get_player_id_from_entrant_id(player2_participant_id) if player2_participant_id else None

            phase_name = ""
            phase_group = node.get('phaseGroup')
            if phase_group:
                display_identifier = phase_group.get('displayIdentifier')
                if display_identifier:
                    phase_name = display_identifier
                if phase_group.get('phase') and phase_group['phase'].get('name'):
                    phase_name = phase_group['phase']['name']
            if not phase_name:
                phase_name = "Desconocido"

            player1_characters, player2_characters = [], []
            if node['games']:
                for game in node['games']:
                    for selection in game['selections']:
                        if str(selection['entrant']['id']) == player1_participant_id:
                            player1_characters.append(selection['character']['id'])
                        elif str(selection['entrant']['id']) == player2_participant_id:
                            player2_characters.append(selection['character']['id'])

            set_data = {
                'id': node['id'],
                'player1_id': player1_id,
                'player2_id': player2_id,
                'player1_name': player1_name,
                'player1_score': player1_score,
                'player2_name': player2_name,
                'player2_score': player2_score,
                'phase_name': phase_name,
                'event_name': node['event']['name'],
                'tournament_name': node['event']['tournament']['name'],
                'player1_characters': player1_characters,
                'player2_characters': player2_characters
            }
            sets.append(set_data)

    while True:
        query = """
        query EventSets($eventId: ID!, $page: Int!, $perPage: Int!) {
            event(id: $eventId) {
                sets(page: $page, perPage: $perPage) {
                    nodes {
                        id
                        displayScore
                        phaseGroup {
                            phase {
                                name
                            }
                            displayIdentifier
                        }
                        event {
                            name
                            tournament {
                                name
                            }
                        }
                        slots {
                            entrant {
                                id
                            }
                        }
                        games {
                            selections {
                                entrant {
                                    id
                                }
                                character {
                                    id
                                }
                            }
                        }
                    }
                }
            }
        }
        """

        variables = {
            'eventId': event_id,
            'page': page_number,
            'perPage': 20
        }

        try:
            response = requests.post(
                startgg_url,
                headers=headers,
                json={'query': query, 'variables': variables}
            )

            response.raise_for_status()
            data = response.json()

            if 'errors' in data:
                raise Exception(', '.join(error['message'] for error in data['errors']))

            event = data.get('data', {}).get('event', {})
            sets_data = event.get('sets', {})
            nodes = sets_data.get('nodes', [])
            process_nodes(nodes)

            if len(nodes) < 20:
                break

            page_number += 1
            delay(1)
        except requests.exceptions.HTTPError as e:
            print(f"Error API EventSets (page {page_number}):", response.status_code, response.text)
            break
        except Exception as e:
            print('Error fetching sets:', e)
            break

    return sets