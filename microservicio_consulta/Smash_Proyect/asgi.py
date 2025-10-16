import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smash_Proyect.settings')

# Preferir Django ASGI por defecto y usar Channels solo si está instalado/configurado
try:
	# Importación perezosa de Channels; si no existe, caemos a Django ASGI
	from channels.routing import get_default_application  # type: ignore
	import django

	django.setup()
	application = get_default_application()
except Exception:
	# Fallback seguro a la aplicación ASGI estándar de Django
	from django.core.asgi import get_asgi_application

	application = get_asgi_application()