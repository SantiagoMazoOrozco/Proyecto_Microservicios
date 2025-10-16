import os
import requests
import traceback
import json
from dotenv import load_dotenv
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import urlparse
import re

load_dotenv()

startgg_url = "https://api.start.gg/gql/alpha"

startgg_key = "3e417c2b55e54203247b7501c15e70ca"  # debe definirse en .env o entorno

if not startgg_key:
    raise ValueError('La clave de la API de Start.gg no está configurada. Define STARTGG_KEY en .env o en las variables de entorno')

def get_event_id(tournament_name, event_name):
    if not tournament_name or not event_name:
        raise ValueError("tournament_name y event_name son obligatorios.")

    event_slug = f"tournament/{tournament_name}/event/{event_name}"

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {startgg_key}'
    }

    query = """
    query EventQuery($slug: String) {
        event(slug: $slug) {
            id
            name
        }
    }
    """

    variables = {'slug': event_slug}

    # Añadido timeout para evitar colgarse indefinidamente
    try:
        response = requests.post(
            startgg_url,
            headers=headers,
            json={'query': query, 'variables': variables},
            timeout=10
        )
    except requests.exceptions.RequestException as e:
        # Propagar para que la vista devuelva 502 con detalles
        raise requests.exceptions.RequestException(f"Error contacting Start.gg: {e}")

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        # Mostrar cuerpo de la respuesta para depuración y lanzar excepción clara
        print("Respuesta de la API (get_event_id):", response.status_code, response.text)
        raise RuntimeError(f"API returned HTTP {response.status_code}: {response.text}")

    data = response.json()

    if 'errors' in data:
        raise RuntimeError(f"API returned errors: {data['errors']}")

    if 'data' not in data or 'event' not in data['data'] or data['data']['event'] is None:
        raise RuntimeError(f"Invalid response structure: {data}")

    return data['data']['event']['id']


# Vista para manejar la solicitud desde el frontend
@csrf_exempt
def get_event_id_view(request):
    # Aceptar params desde query string, form-data o JSON body
    tournament_name = request.GET.get('tournament_name') or request.GET.get('tournament') or request.GET.get('tournamentSlug')
    event_name = request.GET.get('event_name') or request.GET.get('event')

    def extract_from_url_field(url_value):
        """Extrae tournament_name y event_name desde un URL de start.gg.

        Soporta URLs como:
        - https://www.start.gg/tournament/<tournament-slug>/event/<event-slug>
        - https://start.gg/tournament/<tournament-slug>/event/<event-slug>/
        """
        if not url_value:
            return None, None
        try:
            parsed = urlparse(url_value)
            path = parsed.path or url_value
            # normalizar y buscar el patrón
            m = re.search(r"/tournament/([^/]+)/event/([^/]+)/?$", path)
            if m:
                return m.group(1), m.group(2)
            # Si no encontramos, intentar buscar en todo el string (por si nos pasaron solo el path)
            m2 = re.search(r"tournament/([^/]+)/event/([^/]+)/?", url_value)
            if m2:
                return m2.group(1), m2.group(2)
        except Exception:
            return None, None
        return None, None

    if request.method == 'POST':
        # intentar extraer de form data
        if not tournament_name:
            tournament_name = request.POST.get('tournament_name') or request.POST.get('tournament') or request.POST.get('tournamentSlug')
        if not event_name:
            event_name = request.POST.get('event_name') or request.POST.get('event')

        # si contenido JSON, intentar parsear
        if (not tournament_name or not event_name) and request.content_type and 'application/json' in request.content_type:
            try:
                body = json.loads(request.body.decode('utf-8') or "{}")
                tournament_name = tournament_name or body.get('tournament_name') or body.get('tournament') or body.get('tournamentSlug')
                event_name = event_name or body.get('event_name') or body.get('event')
                # support full URL fields
                if (not tournament_name or not event_name):
                    url_val = body.get('url') or body.get('event_url') or body.get('link')
                    t_from_url, e_from_url = extract_from_url_field(url_val)
                    tournament_name = tournament_name or t_from_url
                    event_name = event_name or e_from_url
            except Exception:
                # no bloqueante: seguiremos con lo que haya
                pass

    # Also accept URL passed via GET or POST form fields (non-JSON)
    if (not tournament_name or not event_name):
        url_val = request.GET.get('url') or request.GET.get('event_url') or request.GET.get('link')
        if not url_val and request.method == 'POST':
            url_val = request.POST.get('url') or request.POST.get('event_url') or request.POST.get('link')
        if url_val:
            t_from_url, e_from_url = extract_from_url_field(url_val)
            tournament_name = tournament_name or t_from_url
            event_name = event_name or e_from_url

    missing = []
    if not tournament_name:
        missing.append('tournament_name (or tournament / tournamentSlug)')
    if not event_name:
        missing.append('event_name (or event)')
    if missing:
        # registrar lo recibido para depuración
        print("get_event_id_view called with:", {
            "method": request.method,
            "GET": dict(request.GET),
            "POST": dict(request.POST),
            "content_type": request.content_type,
            "body_preview": (request.body.decode('utf-8')[:100] if request.body else "")
        })
        return JsonResponse({"error": "Missing parameters", "missing": missing}, status=400)

    try:
        event_id = get_event_id(tournament_name, event_name)
        return JsonResponse({"event_id": event_id}, status=200)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except RuntimeError as e:
        print("RuntimeError in get_event_id_view:", str(e))
        traceback.print_exc()
        return JsonResponse({"error": "Upstream API error", "details": str(e)}, status=502)
    except requests.exceptions.RequestException as e:
        print("RequestException in get_event_id_view:", str(e))
        traceback.print_exc()
        return JsonResponse({"error": "Request error contacting upstream API", "details": str(e)}, status=502)
    except Exception as e:
        print("Unexpected exception in get_event_id_view:", str(e))
        traceback.print_exc()
        return JsonResponse({"error": "Internal server error", "details": str(e)}, status=500)


def test_get_event_id():
    tournament_name = "eje-smash-7"
    event_name = "singles"

    try:
        event_id = get_event_id(tournament_name, event_name)
        print(f"Event ID: {event_id}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_get_event_id()