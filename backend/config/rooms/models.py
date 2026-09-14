import random
from django.db import models
import uuid


def generate_unique_room_code():
    characters = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    length = 5

    while True:
        code ="".join(random.choices(characters, k=length))
        if not Room.objects.filter(code=code).exists():
            return code


class Room(models.Model):
    code = models.CharField(
        max_length=10,
        unique=True,
        default=generate_unique_room_code,  # <-- Added default here
    )
    created_at = models.DateTimeField(auto_now_add=True)  # <-- Added created_at

    def __str__(self):
        return self.code


class Player(models.Model):
    player_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="players")
    nickname = models.CharField(max_length=50)
    is_host = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nickname} ({self.room.code})"