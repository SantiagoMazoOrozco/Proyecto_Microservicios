from django.urls import path
from .getEventId import get_event_id_view

urlpatterns = [
    path('get-event-id/', get_event_id_view, name='get_event_id'),
]
