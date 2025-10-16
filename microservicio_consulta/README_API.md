API-only microservice instructions

Este repositorio ha sido adaptado para exponer endpoints JSON-only que pueden consumirse con herramientas como Thunder Client.

Rutas principales (JSON):
- GET /health/ -> Estado del servicio
- POST /api/get-event-id/ -> {"tournament_name": "...", "event_name": "..."}
- GET /api/get-event-info/?event_id=12345
- POST /api/get-player-info/ -> soporta parámetros en GET, POST form o JSON
- POST /api/get-sets-by-tournament/ -> {"event_id": "...", "limit": 10}

Cómo ejecutar localmente (Windows PowerShell):
1) Crear un entorno virtual y activar:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2) Instalar dependencias:

```powershell
pip install -r requirements.txt
```

3) Ejecutar migraciones (si usas la DB incluida):

```powershell
python manage.py migrate
```

4) Ejecutar el servidor de desarrollo:

```powershell
python manage.py runserver
```

Probar con Thunder Client (o curl/postman):
- Health: GET http://127.0.0.1:8000/health/
- Obtener event id (POST JSON, acepta URL completo): POST http://127.0.0.1:8000/api/get-event-id/ Content-Type: application/json Body: {"url":"https://www.start.gg/tournament/tropel-en-el-cafetal-iii/event/tropel-en-el-cafetal-iii"}

Notas:
- Las claves de la API externa (start.gg) están incluidas en módulos `Consultas/api/*` como constantes para desarrollo. Para producción, mueve estas claves a variables de entorno o `.env`.
- Las rutas de UI se han movido a `/web/` para separar la interfaz de plantilla del microservicio JSON.
- Si necesitas exponer más endpoints revisa `Consultas/api_only_urls.py` y las vistas en `Consultas/api/` y `Consultas/views.py`.
