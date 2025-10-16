from django.test import TestCase
from .models import Tournament, Event, Player, Set
from .views import get_event_results  # Importar la función

class MyAppTests(TestCase):
    def setUp(self):
        # Crear datos de prueba
        tournament = Tournament.objects.create(name="Test Tournament")
        event = Event.objects.create(name="Test Event", tournament=tournament)
        player = Player.objects.create(name="Test Player")
        Set.objects.create(player=player, event=event, result="Win")

    def test_get_event_results(self):
        event = Event.objects.get(name="Test Event")
        results = get_event_results(event.id)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['player__name'], "Test Player")
        self.assertEqual(results[0]['result'], "Win")