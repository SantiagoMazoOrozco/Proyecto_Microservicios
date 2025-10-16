import requests
import os
from dotenv import load_dotenv

load_dotenv()

startgg_url = "https://api.start.gg/gql/alpha"
startgg_key = "3e417c2b55e54203247b7501c15e70ca"

def get_set_info(set_id):
    if not set_id:
        raise ValueError("El set_id es requerido.")
    try:
        set_id_int = int(set_id)
    except Exception:
        raise ValueError("El set_id debe ser un número entero válido.")

    query = """
    query GetSetById($setId: ID!) {
      set(id: $setId) {
        id
        fullRoundText
        round
        winnerId
        slots {
          entrant {
            id
            name
            participants {
              player {
                id
                gamerTag
              }
            }
          }
        }
        games {
          winnerId
          orderNum
          selections {
            entrant {
              id
              name
              participants {
                player {
                  id
                  gamerTag
                }
              }
            }
            character {
              id
              name
            }
          }
        }
        event {
          name
          tournament {
            name
          }
        }
        phaseGroup {
          displayIdentifier
          phase {
            name
          }
        }
      }
    }
    """
    variables = {"setId": set_id_int}
    resp = requests.post(
        startgg_url,
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {startgg_key}'},
        json={'query': query, 'variables': variables}
    )
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("Respuesta de la API:", resp.text)
        raise e

    data = resp.json()
    return data.get('data', {}).get('set')

if __name__ == "__main__":
    set_id = input("Ingresa el setId de start.gg: ")
    set_info = get_set_info(set_id)
    import json
    print(json.dumps(set_info, indent=2, ensure_ascii=False))
