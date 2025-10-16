from django.db import models

# Modelo mínimo Character: expone 'name' y 'game' para satisfacer admin/forms que los referencian.
class Character(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    # campo adicional 'game' que algunos admin o list_display esperan
    game = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'Character_Ssbu'

    def __str__(self):
        return self.name or str(self.id)

# Modelo Player mínimo con FK opcional a Character y campos nullables.
class Player(models.Model):
    # si quieres mapear al ID de start.gg, usa BigIntegerField; ajusta según tu DB
    id = models.BigIntegerField(db_column='ID', primary_key=True)
    gamertag = models.CharField(db_column='Gamertag', max_length=200, null=True, blank=True)
    slug = models.CharField(db_column='Slug', max_length=200, null=True, blank=True)
    prefijo = models.CharField(db_column='Prefijo', max_length=200, null=True, blank=True)
    nombre = models.CharField(db_column='Nombre', max_length=200, null=True, blank=True)
    pais = models.CharField(db_column='Pais', max_length=100, null=True, blank=True)
    departamento = models.CharField(db_column='Departamento', max_length=100, null=True, blank=True)
    region = models.CharField(db_column='Region', max_length=100, null=True, blank=True)
    ciudad = models.CharField(db_column='Ciudad', max_length=100, null=True, blank=True)
    twitter = models.CharField(db_column='Twitter', max_length=200, null=True, blank=True)
    discord = models.CharField(db_column='Discord', max_length=200, null=True, blank=True)
    twitch = models.CharField(db_column='Twitch', max_length=200, null=True, blank=True)

    # campos que tu forms/admin referenciaban anteriormente
    main_character = models.CharField(db_column='Main_Character', max_length=100, null=True, blank=True)
    secundary_character = models.CharField(db_column='Secundary_Character', max_length=100, null=True, blank=True)

    # FK opcional hacia Character para evitar errores si el admin intenta resolver relaciones
    main_character_fk = models.ForeignKey(
        Character,
        db_column='main_character_id',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='players_main_character'
    )

    profile_image_url = models.CharField(db_column='profile_image_url', max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'Colombia_Players'

    def __str__(self):
        return self.gamertag or self.nombre or str(self.id)

class CharacterSkin(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='skins')
    skin_number = models.IntegerField()
    skin_name = models.CharField(max_length=100, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)

    class Meta:
        unique_together = ('character', 'skin_number')
        ordering = ['skin_number']

    def __str__(self):
        return f"{self.character.name} - Skin {self.skin_number}"

class Tournament(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    tournament_name = models.CharField(max_length=255, null=True, blank=True)
    winner = models.CharField(max_length=255, null=True, blank=True)
    attendees = models.IntegerField(null=True, blank=True)
    region = models.CharField(max_length=255, null=True, blank=True)
    pais = models.CharField(max_length=255, null=True, blank=True)
    departamento = models.CharField(max_length=255, null=True, blank=True)
    ciudad = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    tier = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'Colombia_Tournament'

    def __str__(self):
        return self.tournament_name or str(self.id)

class TournamentParticipant(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    participant_id = models.BigIntegerField()
    gamertag = models.CharField(max_length=100)

    class Meta:
        unique_together = ('tournament', 'player')
        db_table = 'Consultas_tournamentparticipant'

    def __str__(self):
        return f"{self.gamertag} @ {self.tournament}"

class Event(models.Model):
    name = models.CharField(max_length=255)
    phase = models.CharField(max_length=100)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.phase} ({self.tournament})"

class Set(models.Model):
    id_torneo = models.CharField(max_length=100, db_column='id_torneo', null=True, blank=True)
    id_set = models.IntegerField(null=True, blank=True, db_column='id_set')
    id_player_1 = models.BigIntegerField(null=True, blank=True, db_column='id_player_1')
    player_1 = models.CharField(max_length=200, null=True, blank=True, db_column='player_1')
    player_1_score = models.IntegerField(null=True, blank=True, db_column='player_1_score')
    id_player_2 = models.BigIntegerField(null=True, blank=True, db_column='id_player_2')
    player_2 = models.CharField(max_length=200, null=True, blank=True, db_column='player_2')
    player_2_score = models.IntegerField(null=True, blank=True, db_column='player_2_score')
    phase = models.CharField(max_length=100, null=True, blank=True)
    event_name = models.CharField(max_length=200, null=True, blank=True)
    tournament_name = models.CharField(max_length=200, null=True, blank=True)
    player_1_characters = models.TextField(null=True, blank=True)
    player_2_characters = models.TextField(null=True, blank=True)
    ronda = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'Colombia_Sets'

    def __str__(self):
        return f"{self.id_torneo}:{self.id_set}"