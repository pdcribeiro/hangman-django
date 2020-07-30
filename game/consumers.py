import datetime
import json
import random

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.db.models import F
from django.utils import timezone

from .models import Game, Player, Word
from .views import validate_player


class RoomConsumer(JsonWebsocketConsumer):
    def connect(self):
        player_id = validate_player(self.scope['session'])

        if player_id is None:
            return

        async_to_sync(self.channel_layer.group_add)('main', self.channel_name)
        self.accept()

        Player.objects.filter(id=player_id).update(active=True)
        print(f"Player with id {player_id} is active.")

        new_game = Player.objects.all().count() == 1
        if new_game:
            game_state = self.start_round(new_game=True)
        else:
            game_state = self.get_game_state()

        self.send_json(game_state)

    # TODO? move to models.py?
    def start_round(self, new_game=False):
        """Starts new game or round and returns game state."""
        session = self.scope['session']

        if new_game:
            game = Game.objects.create()
            session['game_id'] = game.id
        else:
            game = Game.objects.get(id=session['game_id']).next_round()

        word = get_word()
        Word.objects.create(word=word, game=game)

        return generate_game_state(game, word)

    # TODO? move to models.py?
    def get_game_state(self):
        """Returns current game state."""
        session = self.scope['session']

        game_id = session.get('game_id')
        if game_id is not None:
            game = Game.objects.get(id=game_id)
        else:
            game = Game.objects.all().first()
            session['game_id'] = game.id

        word = Word.objects.filter(game=game).first().word

        return generate_game_state(game, word)

    def receive_json(self, data):
        """Receives letter and broadcasts new game state."""
        player_id = validate_player(self.scope['session'])
        if player_id is None:
            return

        letter = data.get('letter')
        if letter is not None:
            self.handle_guess(player_id, letter)

    # TODO? move to models.py?
    def handle_guess(self, player_id, letter):
        # TODO sanitize letter
        parsed_letter = letter.upper()
        game_state = self.get_game_state()
        session = self.scope['session']

        # Ignore repeated letters.
        if parsed_letter in game_state['letters']:
            return

        # Append to guesses.
        game_state['letters'] += parsed_letter
        Game.objects.filter(id=session['game_id']).update(
            letters=game_state['letters'])

        # Decrement chances on wrong guess.
        if parsed_letter not in game_state['word']:
            game_state['chances'] -= 1
            Game.objects.filter(id=session['game_id']).update(
                chances=game_state['chances'])

        self.broadcast_game_state(game_state)

        # Handle game over.
        win = not any([l not in game_state['letters']
                       for l in game_state['word']])
        winner = win and Player.objects.get(id=player_id).username
        if winner or game_state['chances'] == 0:
            game_state = self.start_round()
            game_state['winner'] = winner or None
            self.broadcast_game_state(game_state)

    def broadcast_game_state(self, game_state):
        msg = {'type': 'game_state', 'game_state': game_state}
        async_to_sync(self.channel_layer.group_send)('main', msg)

    def game_state(self, event):
        self.send_json(event['game_state'])

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            'main', self.channel_name)

        player_id = validate_player(self.scope['session'])

        if player_id is not None:
            Player.objects.filter(id=player_id).update(active=False)
            print(f"Player with id {player_id} is inactive.")

        # Kick inactive players.
        now = timezone.now()
        one_day_ago = now - datetime.timedelta(days=1)
        Player.objects.filter(active=False, joined__lt=one_day_ago).delete()

        # Set game end timestamp
        last_player = Player.objects.count() == 1
        game_id = self.scope['session'].get('game_id')
        if last_player and game_id is not None:
            Game.objects.filter(id=game_id).update(ended=now)


# TODO? move to models.py?
def generate_game_state(game, word):
    return {'word': word, 'chances': game.chances, 'letters': game.letters}


def get_word():
    return random.choice([
        'elephant', 'giraffe', 'pig', 'bear', 'dog', 'cat'
    ]).upper()
