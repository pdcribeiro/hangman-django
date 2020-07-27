import datetime
import functools

from django.shortcuts import redirect, render
from django.utils import timezone

from .models import Game, Player


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(request, *args, **kwargs):
        if request.session.get('player_id') is None:
            return redirect('lobby')

        return view(request, *args, **kwargs)

    return wrapped_view


def lobby(request):
    if request.session.get('player_id') is not None:
        return redirect('room')

    errors = []

    if request.method == 'POST':
        # TODO sanitize username
        username = request.POST.get('username')

        if username is None:
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
def leave(request):
    player_id = request.session.get('player_id')
    if player_id is not None:
        del request.session['player_id']
        try:
            player = Player.objects.get(id=player_id)
            player.delete()
            print(f"Player '{player.username}' left the game.")
        except Player.DoesNotExist:
            pass

    check_end_game(request.session.get('game_id'))
    return redirect('lobby')


def check_end_game(game_id):
    now = timezone.now()
    yesterday = now - datetime.timedelta(days=1)
    Player.objects.filter(active=False, joined__lt=yesterday).delete()

    # Set game end timestamp
    players = Player.objects.count()
    if players == 0 and game_id is not None:  # players == 1?
        Game.objects.filter(id=game_id).update(ended=now)
