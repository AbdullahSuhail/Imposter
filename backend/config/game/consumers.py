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

        if data.get("type") == "next_turn":

            print("CONSUMER OF NEXT TURN")

            game_state = GameState.objects.get(
            room=self.player.room
           )

            # Make sure only the current player can press NEXT
            if game_state.current_player != self.player:
                return

            players = list(
                self.player.room.players.order_by("joined_at")
            )

            current_index = players.index(
                game_state.current_player
            )

            # Check if this was the last player
            if current_index == len(players) - 1:

                game_state.phase = GameState.Phase.VOTING
                game_state.current_player = None
                game_state.save()

                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        "type": "voting_started"
                    }
                )

            else:
                    
                    next_player = players[current_index + 1]
                    game_state.current_player = next_player
                    game_state.save()

                    async_to_sync(self.channel_layer.group_send)(
                        self.room_group_name,
                        {
                            "type": "turn_changed",
                            "player_id": str(next_player.player_id),
                            "nickname": next_player.nickname
                        }
                    )

        if data.get("type") == "clue_connected":

            game_state = GameState.objects.get(
                room=self.player.room
            )

            self.send(text_data=json.dumps({
                "type": "current_player",
                "player_id": str(game_state.current_player.player_id),
                "nickname": game_state.current_player.nickname
            }))

        if data.get("type") == "startClue":

           
            if not self.player.is_host:
                return

            players=list(self.player.room.players.order_by("joined_at"))
            first_player = players[0]


            game_state = GameState.objects.get(
                room=self.player.room
            )

            print("The first player is ",first_player)

            game_state.phase = GameState.Phase.CLUE
            game_state.current_player = first_player
            game_state.save()

            firstplayer=players[0]

            print("CONSUMER STARTCLUE PHASE")

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    "type": "clue_started",
                    "player_id": str(first_player.player_id),
                    "nickname": first_player.nickname
                }
            )


    def clue_started(self, event):

        print("CLUE_STARTED HANDLER CALLED")

        self.send(text_data=json.dumps({
            "type": "clue_started",
            "player_id": event["player_id"],
            "nickname": event["nickname"]
        }))