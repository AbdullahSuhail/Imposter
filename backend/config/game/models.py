from django.db import models
from rooms.models import Room# Create your models here.
class GameState(models.Model):

    class Phase(models.TextChoices):
        LOBBY = "LOBBY"
        WORD_REVEAL = "WORD_REVEAL"
        CLUE = "CLUE"
        VOTING = "VOTING"
        RESULT = "RESULT"
        GAME_OVER = "GAME_OVER"

    room = models.OneToOneField(
        Room,
        on_delete=models.CASCADE,
        related_name="game_state"
    )

    current_player = models.ForeignKey(
    "rooms.Player",
    on_delete=models.SET_NULL,
    null=True,
    blank=True
)

    phase = models.CharField(
        max_length=20,
        choices=Phase.choices,
        default=Phase.LOBBY
    )

    created_at = models.DateTimeField(auto_now_add=True)


# game/models.py

from django.db import models


class WordPair(models.Model):
    word1 = models.CharField(max_length=100)
    word2 = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.word1} | {self.word2}"

class PlayerWord(models.Model):
    player = models.ForeignKey(
        "rooms.Player",
        on_delete=models.CASCADE
    )
    word = models.CharField(max_length=100)