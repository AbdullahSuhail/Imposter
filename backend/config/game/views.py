from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from rooms.models import Room
from django.shortcuts import render

def game(request, code):
    room = get_object_or_404(Room, code=code)

    session_player_id = request.session.get("player_id")

    current_player = room.players.filter(
        player_id=session_player_id
    ).first()

    is_host = current_player.is_host if current_player else False

    context = {
        'code': code,
        'room': room,
        'is_host': is_host,
    }

    return render(request, 'game/reveal.html', context)


def clue(request,code):
    # is_host = current_player.is_host if current_player else False
    room = get_object_or_404(Room, code=code)

    context = {
        'code': code,
        'room': room,
        # 'is_host': is_host,
    }
    

    room = get_object_or_404(Room, code=code)
 
    return render(request, 'game/clue.html' ,context)
   
    