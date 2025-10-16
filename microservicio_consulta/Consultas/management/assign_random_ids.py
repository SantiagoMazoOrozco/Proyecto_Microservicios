from django.core.management.base import BaseCommand
from myapp.models import Player
import uuid

class Command(BaseCommand):
    help = 'Asigna IDs aleatorios a los jugadores que no tienen un ID asignado'

    def handle(self, *args, **kwargs):
        players_without_id = Player.objects.filter(id__isnull=True)
        for player in players_without_id:
            player.id = uuid.uuid4()
            player.save()
        self.stdout.write(self.style.SUCCESS('IDs aleatorios asignados a los jugadores sin ID'))