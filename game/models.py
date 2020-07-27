from django.db import models


class Player(models.Model):
    username = models.CharField(max_length=50, unique=True)
    active = models.BooleanField(default=False)
    joined = models.DateTimeField(auto_now_add=True)


class Game(models.Model):
    chances = models.IntegerField(default=6)
    letters = models.CharField(max_length=26)
    rounds = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    ended = models.DateTimeField()


class Word(models.Model):
    word = models.CharField(max_length=50)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
