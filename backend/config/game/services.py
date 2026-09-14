import random
from .models import WordPair, PlayerWord


def start_game(room):

    print("WE HAVE REACHED START GAME FUNCTION")

    players = list(room.players.all())
    print("BEFORE WORD PAIR CHOICE")

    word_pair = random.choice(list(WordPair.objects.all()))
    print("BEFORE IMPOST CHOICE")

    imposter = random.choice(players)

    PlayerWord.objects.filter(player__room=room).delete()
    print("BEFORE THE FOR LOOP")
    for player in players:
        if player == imposter:
            word = word_pair.word2
        else:
            word = word_pair.word1

        PlayerWord.objects.create(
            player=player,
            word=word
        )

    print("START_GAME FINISHED")