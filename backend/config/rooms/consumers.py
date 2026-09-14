# from channels.generic.websocket import WebsocketConsumer

import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Player ,Room
from game.models import GameState
from game.services import start_game

class RoomConsumer(WebsocketConsumer):

    def connect(self):
        self.room_code = self.scope["url_route"]["kwargs"]["code"]
        self.room_group_name = f"room_{self.room_code}"

        # Must wrap channel layer calls in async_to_sync
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()
        self.broadcast_player_list()

    
  
    def player_joined(self, event):
        self.send(text_data=event["nickname"])



    def receive(self, text_data):
        data = json.loads(text_data)

        session = self.scope.get("session")

        player_id_val = session.get("player_id") if session else None

        # PLAYER LEAVING LOGIC 
        if data.get("type") == "leave":
            if player_id_val:
                try:
                    player = Player.objects.get(player_id=player_id_val)
                    washost=player.is_host
                    roomofhost=player.room
                    player.delete()   ## DELETING THE PLAYER FROM DB
                    if washost:
                        nextHost = (
                            Player.objects.filter(room=roomofhost)
                            .order_by("joined_at")   ## GETTTING THE PLAYER NEXT IN LINE FOR MAKING THE HOST 
                            .first()
                        )
                        if nextHost:
                            nextHost.is_host = True
                            nextHost.save()
                            
                except Player.DoesNotExist:
                    print(f"Player with id {player_id_val} not found in DB.")

            if session and "player_id" in session:
                del session["player_id"]
                session.save()

            self.broadcast_player_list()

            self.close()

        if data.get("type")=="start_game":
             print("GAME STARTTTTTTTT")

             if player_id_val:
                print("ENTER IF ")
                try:

                    player=Player.objects.get(
                        player_id=player_id_val
                    )
                    # pass
                    print("BEFORE PASS")

                    game_state, created = GameState.objects.get_or_create(
                    room=player.room
                     )

        # 4. Change phase
                    print("CHANGEG PHASE ")

                    game_state.phase = GameState.Phase.WORD_REVEAL
                    game_state.save()
                    print("BEFORE STARTGAME")

                    start_game(player.room)


                    print("AFTER STARTGAME")

                    if player.is_host:

                        async_to_sync(
                            self.channel_layer.group_send
                        )(
                            self.room_group_name,
                            {
                                "type":"game_started"
                            })
                except:
                    pass
             
        

        
 
  


    def disconnect(self, close_code):

        pass


        
 

    def player_left(self,event):
        self.send(text_data=event["nickname"])


    def broadcast_player_list(self):
    
        try:
            room = Room.objects.get(code=self.room_code)
            players = list(
                room.players.all().order_by("joined_at").values("nickname", "is_host","player_id")
            )
            for player in players:     ## DOING AS WE CANNOT CONVERT UUUID IN JSON FORMAT
                player["player_id"] = str(player["player_id"])
        except Room.DoesNotExist:
            players = []

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "send_player_list",
                "players": players
            }
        )

    def send_player_list(self, event):
                
                self.send(text_data=json.dumps({
                    "type": "update_player_list",
                    "players": event["players"]
                }))

    def game_started(self, event):

        self.send(text_data=json.dumps({
            "type": "game_started"
        }))
                