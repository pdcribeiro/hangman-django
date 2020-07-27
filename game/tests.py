from django.test import Client, TestCase
from django.urls import reverse

from .models import Player


class ViewTests(TestCase):
    USERNAME = 'player'
    PLAYER2_USERNAME = 'player2'
    MISSING_USERNAME_ERROR = 'Please provide a username.'
    DUPLICATE_USERNAME_ERROR = f"'{USERNAME}' is already taken."
    ONE_PLAYER_WAITING_MESSAGE = 'There is 1 player waiting for you!'

    def test_root_url(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/lobby.html')

    def test_lobby_view(self):
        response = self.client.get(reverse('lobby'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/lobby.html')

    def test_lobby_view_shows_no_messages(self):
        response = self.client.get(reverse('lobby'))
        self.assertEqual(response.context.get('players'), 0)
        self.assertEqual(response.context.get('errors'), [])
        self.assertNotContains(response, 'waiting for you')
        self.assertNotContains(response, '<div class="error">', html=True)

    def test_join_game_redirects_to_room(self):
        response = join_game(self.client, self.USERNAME)
        response = self.assertRedirects(response, '/game/')
        self.assertTemplateUsed(response, 'game/room.html')

    def test_join_game_adds_player_to_db(self):
        self.assertEqual(count_players(username=self.USERNAME), 0)
        join_game(self.client, self.USERNAME)
        self.assertEqual(count_players(username=self.USERNAME), 1)

    def test_join_game_adds_player_id_to_session(self):
        join_game(self.client, self.USERNAME)
        self.assertNotEqual(self.client.session.get('player_id'), None)

    def test_join_game_without_username_field(self):
        self.assertEqual(count_players(username=self.USERNAME), 0)
        response = self.client.post(reverse('lobby'))
        self.assertEqual(response.context.get('errors'),
                         [self.MISSING_USERNAME_ERROR])
        self.assertTemplateUsed(response, 'game/lobby.html')
        self.assertContains(response, self.MISSING_USERNAME_ERROR)
        self.assertEqual(count_players(username=self.USERNAME), 0)
        self.assertEqual(self.client.session.get('player_id'), None)

    def test_join_game_with_empty_username(self):
        self.assertEqual(count_players(username=self.USERNAME), 0)
        response = join_game(self.client, '')
        self.assertEqual(response.context.get('errors'),
                         [self.MISSING_USERNAME_ERROR])
        self.assertTemplateUsed(response, 'game/lobby.html')
        self.assertContains(response, self.MISSING_USERNAME_ERROR)
        self.assertEqual(count_players(username=self.USERNAME), 0)
        self.assertEqual(self.client.session.get('player_id'), None)

    def test_join_game_with_duplicate_username(self):
        self.assertEqual(count_players(username=self.USERNAME), 0)
        join_game(self.client, self.USERNAME)
        player2 = Client()
        response = join_game(player2, self.USERNAME)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('errors'),
                         [self.DUPLICATE_USERNAME_ERROR])
        self.assertTemplateUsed(response, 'game/lobby.html')
        html = response.content.decode()
        self.assertInHTML(self.DUPLICATE_USERNAME_ERROR, html)
        self.assertEqual(count_players(username=self.USERNAME), 1)
        self.assertEqual(player2.session.get('player_id'), None)

    def test_lobby_view_after_join_game_redirects_to_room(self):
        join_game(self.client, self.USERNAME)
        response = self.client.get(reverse('lobby'))
        self.assertRedirects(response, '/game/')

    # TODO
    def test_lobby_view_after_join_game_shows_players_waiting_message(self):
        join_game(self.client, self.USERNAME)
        response = Client().get(reverse('lobby'))
        # self.assertEqual(response.context.get('players'), 1)
        # self.assertContains(response, self.ONE_PLAYER_WAITING_MESSAGE)

    def test_room_view_redirects_to_lobby(self):
        response = self.client.get(reverse('room'))
        self.assertRedirects(response, '/')

    def test_room_view_after_join_game(self):
        join_game(self.client, self.USERNAME)
        response = self.client.get(reverse('room'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/room.html')

    def test_leave_view_redirects_to_lobby(self):
        response = self.client.get(reverse('leave'))
        self.assertRedirects(response, '/')

    def test_leave_game_after_join_game_redirects_to_lobby(self):
        join_game(self.client, self.USERNAME)
        response = self.client.get(reverse('leave'))
        response = self.assertRedirects(response, '/')
        self.assertTemplateUsed(response, 'game/lobby.html')

    def test_leave_game_removes_player_from_db(self):
        join_game(self.client, self.USERNAME)
        self.client.get(reverse('leave'))
        self.assertEqual(count_players(username=self.USERNAME), 0)

    def test_leave_game_removes_player_id_from_session(self):
        join_game(self.client, self.USERNAME)
        self.client.get(reverse('leave'))
        self.assertEqual(self.client.session.get('player_id'), None)

    # TODO
    def test_leave_game_removes_inactive_players_from_db(self):
        pass

    # TODO
    def test_leave_game_ends_game_when_player_is_last(self):
        # join_game(self.client, self.USERNAME)
        # join_game(Client(), self.PLAYER2_USERNAME)
        # self.client.get(reverse('leave'))
        pass

    # TODO
    def test_leave_game_does_not_end_game_when_player_is_not_last(self):
        pass


def join_game(client, username):
    return client.post(reverse('lobby'), {'username': username})


def count_players(**kwargs):
    return Player.objects.filter(**kwargs).count()
