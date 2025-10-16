# CSSSBUBD/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # API-only endpoints (JSON)
    path('api/', include('Consultas.api_only_urls')),
    # Expose API at root as well for microservice behavior
    path('', include('Consultas.api_only_urls')),
]
