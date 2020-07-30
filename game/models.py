from django.db import models


class Player(models.Model):
    username = models.CharField(max_length=50, unique=True)
    joined = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)  #TODO change into DateTimeField(null=True) to improve check_end_game() (set on disconnect)

    class Meta:
        ordering = ['-joined']
    
    def __str__(self):
        return self.username


class Game(models.Model):
    INIT_CHANCES = 6
    chances = models.IntegerField(default=INIT_CHANCES)
    letters = models.CharField(max_length=26, default='')
    rounds = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    ended = models.DateTimeField(null=True)

    class Meta:
        ordering = ['-created']
    
    def __str__(self):
        return f'{self.id} | {self.created}'

    def next_round(self):
        self.chances = Game.INIT_CHANCES
        self.letters = ''
        self.rounds += 1
        self.save()
        return self


class Word(models.Model):
    word = models.CharField(max_length=50)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    class Meta:
        ordering = ['game', '-id']
    
    def __str__(self):
        return self.word
