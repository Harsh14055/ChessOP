from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    elo_rating = models.IntegerField(default=1200)
    guess_the_move_score = models.IntegerField(default=0)
    board_vision_accuracy = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.user.username} (Elo: {self.elo_rating})"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

class Game(models.Model):
    room_code = models.CharField(max_length=10, unique=True)
    white_player = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='games_white')
    black_player = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='games_black')
    fen = models.CharField(max_length=100, default='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
    moves_list = models.JSONField(default=list)
    pgn = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, default='WAITING') # WAITING, IN_PROGRESS, COMPLETED
    winner = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        w = self.white_player.username if self.white_player else "Waiting"
        b = self.black_player.username if self.black_player else "Waiting"
        return f"Room {self.room_code}: {w} vs {b}"

class Flashcard(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    fen = models.CharField(max_length=100)
    difficulty = models.CharField(
        max_length=10,
        choices=[('EASY', 'Easy'), ('MEDIUM', 'Medium'), ('HARD', 'Hard')],
        default='MEDIUM'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title or 'Position'} ({self.difficulty})"

class FlashcardPosition(models.Model):
    fen = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=20, default="medium")  # easy, medium, hard
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Position [{self.difficulty}]: {self.fen}"

class MasterGame(models.Model):
    title = models.CharField(max_length=255)
    pgn = models.TextField()
    decision_ply = models.IntegerField(default=24)
    gm_move_san = models.CharField(max_length=10, default="")
    gm_idea = models.TextField(blank=True, null=True, default="")
    game_story = models.TextField(blank=True, null=True, default="")

    def __str__(self):
        return self.title