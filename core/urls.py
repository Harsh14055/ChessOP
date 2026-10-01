from django.urls import path
from . import views
from .views import (
    RegisterView,
    UserProfileView,
    CreateOrListGameView,
    FlashcardListView,
    GameDetailView,
)

urlpatterns = [
    # Main Navigation / Home Landing Page
    path('', views.home_view, name='home'),
    path('lobby/', views.lobby_view, name='lobby'),  # Ensure this matches your view function name (lobby_view vs lobby)

    # Template Session Auth Views
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='template_login'),
    path('logout/', views.logout_view, name='template_logout'),

    # Core Features (HTML Pages)
    path('gm-trainer/', views.gm_trainer_page, name='gm_trainer'),
    path('flashcards/', views.flashcards_page, name='flashcards'),
    path('create-room/', views.create_room, name='create_room'),
    path('play/<str:room_code>/', views.play_game_view, name='play_game'),

    # REST API Endpoints for Dynamic Frontend
    path('api/flashcards/random/', views.RandomFlashcardView.as_view(), name='random_flashcard'),
    path('api/gm-trainer/puzzle/', views.GMTrainerPuzzleView.as_view(), name='gm_puzzle'),

    # REST API / JWT Authentication & Game Management
    path('auth/register/', RegisterView.as_view(), name='api_register'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('games/', CreateOrListGameView.as_view(), name='create_or_list_games'),
    path('games/<str:room_code>/', GameDetailView.as_view(), name='game_detail'),
    path('api/flashcards/', FlashcardListView.as_view(), name='flashcard_list'),
]