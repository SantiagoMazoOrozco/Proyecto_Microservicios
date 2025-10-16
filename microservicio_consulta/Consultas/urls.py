from django.urls import path
from django.urls import path, include
from . import views

# API-only URLS: delegamos a api_only_urls para mantener un único lugar
# donde se definen los endpoints JSON que sirven al microservicio.
urlpatterns = [
    path('', include('Consultas.api_only_urls')),
]
