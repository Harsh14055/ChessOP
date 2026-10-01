from django.contrib import admin
from .models import UserProfile, Game, MasterGame, FlashcardPosition

admin.site.register(UserProfile)
admin.site.register(Game)
admin.site.register(MasterGame)
admin.site.register(FlashcardPosition)