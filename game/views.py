# import datetime
import functools

from django.shortcuts import redirect, render
# from django.utils import timezone

from .models import Game, Player


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(request, *args, **kwargs):
        if validate_player(request.session) is None:
            return redirect('lobby')
        else:
            return view(request, *args, **kwargs)

    return wrapped_view


def validate_player(session):
    player_id = session.get('player_id')
    if player_id is None:
        return None

    player_exists = Player.objects.filter(id=player_id).count() == 1
    if not player_exists:
        del session['player_id']
        return None

    return player_id


def lobby(request):
    if request.session.get('player_id') is not None:
        return redirect('room')

    errors = []

    if request.method == 'POST':
        # TODO sanitize username
        username = request.POST.get('username')

        if not username:
            errors.append('Please provide a username.')
        elif Player.objects.filter(username=username).count() > 0:
            errors.append(f"'{username}' is already taken.")

        if not errors:
            player = Player.objects.create(username=username)
            request.session['player_id'] = player.id

            print(f"Player '{username}' joined the game.")
            return redirect('room')

    context = {
        'players': Player.objects.filter(active=True).count(),
        'errors': errors,
    }

    return render(request, 'game/lobby.html', context)


@login_required
def room(request):
    return render(request, 'game/room.html')


@login_required
def leave(request, player=None):
    player_id = request.session.get('player_id')
    del request.session['player_id']
    Player.objects.filter(id=player_id).delete()
    print(f"Player with id {player_id} left the game.")

    # check_end_game(request.session.get('game_id'))
    return redirect('lobby')
