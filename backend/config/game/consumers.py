from channels.generic.websocket import WebsocketConsumer
from rooms.models import Player
import json
from .models import PlayerWord ,GameState
from asgiref.sync import async_to_sync

class GameConsumer(WebsocketConsumer):

    def connect(self):

        # Get room code
        self.room_code = self.scope["url_route"]["kwargs"]["code"]
        self.room_group_name = f"game_{self.room_code}"

        # Get current player's ID from session
        player_id = self.scope["session"].get("player_id")

        # Find that player in database
        self.player = Player.objects.get(player_id=player_id)

        # JOIN THE GROUP
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

        player_word = PlayerWord.objects.get(
            player=self.player
        )

        # Send only to this player
        self.send(text_data=json.dumps({
            "type": "word",
            "word": player_word.word
        }))

        print("GAME SOCKET CONNECTED")
        print("PLAYER:", self.player.nickname)
        print("PLAYER ID:", self.player.player_id)
        print("GROUP:", self.room_group_name)

    def receive(self, text_data):
        print("WE HAVE ENTERED RECEIVE")

        data = json.loads(text_data)

        print("ENTER THIS AFTER DONE ", text_data)

        if data.get("type") == "startClue":

            # print("ENTER if condition")
            if not self.player.is_host:
                return

            players=list(self.player.room.players.order_by("joined_at"))
            first_player = players[0]


            game_state = GameState.objects.get(
                room=self.player.room
            )

            game_state.phase = GameState.Phase.CLUE
            game_state.current_player = first_player
            game_state.save()

            firstplayer=players[0]

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    "type": "clue_started",
                    "player_id": str(first_player.player_id),
                    "nickname": first_player.nickname
                }
            )


    def clue_started(self, event):

        print("CLUE_STATED HANDLER CALLED")

        self.send(text_data=json.dumps({
            "type": "clue_started"
        }))