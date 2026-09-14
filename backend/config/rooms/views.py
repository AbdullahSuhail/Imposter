import uuid

from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Player
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def get_player_id(request):
    if 'player_id' not in request.session:
        request.session['player_id'] = str(uuid.uuid4())

    return request.session['player_id']


def home_view(request):
    error = None

    if request.method == 'POST' and 'join_room' in request.POST:
        nickname = request.POST.get('nickname', '').strip()
        code = request.POST.get('code', '').strip().upper()

        if not nickname:
            error = "Please enter a nickname."
        elif not code:
            error = "Please enter a room code."
        else:
            try:
                room = Room.objects.get(code=code)

                player_id = get_player_id(request)

                # Create this browser's player
                Player.objects.update_or_create(
                    player_id=player_id,
          defaults={
        'room': room,
        'nickname': nickname,
        'is_host': False,  # Updated safely inside defaults
    }
                )

                # channel_layer = get_channel_layer()

                # async_to_sync(channel_layer.group_send)(
                #     f"room_{room.code}",
                #     {
                #         "type": "player_joined",
                #         "nickname":  nickname
                #     }
                # )

                return redirect('room_detail', code=room.code)

            except Room.DoesNotExist:
                error = f"Room '{code}' not found."

    return render(request, 'rooms/home.html', {'error': error})


def create_room_view(request):
    if request.method == 'POST':
        nickname = request.POST.get('nickname', '').strip() or 'Host'

        room = Room.objects.create()

        player_id = get_player_id(request)

        Player.objects.update_or_create(
            player_id=player_id,
            room=room,
            nickname=nickname,
            is_host=True
        )

        return redirect('room_detail', code=room.code)

    return redirect('home')


def room_detail_view(request, code):
    room = get_object_or_404(Room, code=code)

    players = room.players.all().order_by('joined_at')

    session_player_id = request.session.get("player_id")

    # Check if the person viewing this page is the host
    current_player = room.players.filter(player_id=session_player_id).first()
    is_host = current_player.is_host if current_player else False



    return render(
        request,
        'rooms/room_detail.html',
        {
            'room': room,
            'players': players,
            "is_host": is_host,
        }
    )