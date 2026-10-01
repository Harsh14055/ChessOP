import json
import uuid
import random
import io
import chess.pgn
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import UserProfile, Game, FlashcardPosition, Flashcard, MasterGame
from .serializers import (
    RegisterSerializer,
    UserProfileSerializer,
    GameSerializer,
    FlashcardPositionSerializer
)
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

from django.shortcuts import render
from .models import Game
from django.db.models import Q

def lobby_view(request):
    # Clean up ancient abandoned rooms (> 1 hour old with missing players)
    expiration_time = timezone.now() - timedelta(hours=1)
    Game.objects.filter(created_at__lt=expiration_time).filter(
        Q(white_player__isnull=True) & Q(black_player__isnull=True)
    ).delete()

    # Fetch only valid rooms where at least one slot is waiting and game isn't finished
    available_rooms = Game.objects.filter(
        status='WAITING'
    ).filter(
        Q(white_player__isnull=True) | Q(black_player__isnull=True)
    ).exclude(
        Q(white_player__isnull=True) & Q(black_player__isnull=True)
    ).order_by('-created_at')

    return render(request, 'core/lobby.html', {'open_games': available_rooms})


def home_view(request):
    return render(request, 'core/home.html')

def lobby(request):
    expiration_time = timezone.now() - timedelta(hours=2)
    Game.objects.filter(created_at__lt=expiration_time).filter(
        Q(status='COMPLETED') | Q(white_player__isnull=True, black_player__isnull=True)
    ).delete()

    available_rooms = Game.objects.filter(
        status='IN_PROGRESS'
    ).filter(
        Q(white_player__isnull=True) | Q(black_player__isnull=True)
    ).order_by('-created_at')

    return render(request, 'core/lobby.html', {'available_rooms': available_rooms})


def create_room(request):
    if request.method == 'POST':
        room_code = str(uuid.uuid4())[:8]
        game = Game.objects.create(
            room_code=room_code,
            white_player=request.user if request.user.is_authenticated else None,
            status='WAITING'
        )
        return JsonResponse({'room_code': room_code})
    return JsonResponse({'error': 'Invalid request'}, status=400)


# ==========================================
# TEMPLATE VIEWS (WEB AUTH & GAME UI)
# ==========================================

def play_game_view(request, room_code):
    game = get_object_or_404(Game, room_code=room_code)
    # MUST BE 'core/play.html', NOT 'core/game.html'
    return render(request, 'core/game.html', {'room_code': room_code})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('create_or_list_games')
        
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('create_or_list_games')
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Check for explicit 'next' parameter in GET or POST
            next_url = request.POST.get('next') or request.GET.get('next')
            
            # If 'next' points to /games/ or is missing, override to home
            if not next_url or next_url == '/games/':
                return redirect('home')
            
            return redirect(next_url)
    else:
        form = AuthenticationForm()

    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('template_login')


@login_required(login_url='template_login')
def game_room(request, room_code):
    return render(request, 'core/game.html', {'room_code': room_code})


def flashcards_page(request):
    flashcards = Flashcard.objects.all().order_by('?')
    fens = [card.fen for card in flashcards]
    
    return render(request, 'core/flashcards.html', {
        'fens_json': json.dumps(fens)
    })


def gm_trainer_page(request):
    games = list(MasterGame.objects.all())
    game = random.choice(games) if games else None
    
    game_data = None
    if game:
        calculated_fen = None
        target_san = game.gm_move_san
        
        # Process PGN using python-chess to compute exact decision FEN
        if game.pgn:
            try:
                pgn_io = io.StringIO(game.pgn)
                parsed_game = chess.pgn.read_game(pgn_io)
                if parsed_game:
                    board = parsed_game.board()
                    ply_counter = 0
                    limit = game.decision_ply if game.decision_ply is not None else 0
                    
                    for move in parsed_game.mainline_moves():
                        if ply_counter >= limit:
                            break
                        board.push(move)
                        ply_counter += 1
                        
                    calculated_fen = board.fen()
            except Exception:
                calculated_fen = None

        game_data = {
            'id': game.id,
            'title': game.title,
            'pgn': game.pgn,
            'decision_ply': game.decision_ply,
            'gm_move_san': target_san,
            'gm_idea': game.gm_idea,
            'game_story': game.game_story,
            'fen': calculated_fen
        }
        
    return render(request, 'core/gm_trainer.html', {
        'game_json': json.dumps(game_data) if game_data else 'null'
    })


def get_random_flashcard(request):
    cards = Flashcard.objects.all().values('id', 'title', 'fen', 'difficulty')
    return JsonResponse(list(cards), safe=False)


# ==========================================
# REST API ENDPOINTS
# ==========================================

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class CreateOrListGameView(generics.ListCreateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        room_code = str(uuid.uuid4())[:8]
        serializer.save(room_code=room_code, white_player=self.request.user)


class GameDetailView(generics.RetrieveUpdateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    lookup_field = 'room_code'
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        game = self.get_object()
        
        if game.black_player is None and game.white_player != request.user:
            game.black_player = request.user
            game.status = 'IN_PROGRESS'
            game.save()
            serializer = self.get_serializer(game)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        return super().patch(request, *args, **kwargs)


class FlashcardListView(generics.ListAPIView):
    queryset = FlashcardPosition.objects.all()
    serializer_class = FlashcardPositionSerializer
    permission_classes = [permissions.AllowAny]


class RandomFlashcardView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        flashcards = list(Flashcard.objects.values('id', 'title', 'fen', 'difficulty'))
        
        if not flashcards:
            sample_positions = [
                {"id": 1, "title": "Ruy Lopez / Italian setup", "fen": "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3", "difficulty": "Medium"},
                {"id": 2, "title": "Queen's Gambit setup", "fen": "rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR b KQkq - 0 2", "difficulty": "Medium"}
            ]
            return Response(sample_positions)
        
        return Response(flashcards)


class GMTrainerPuzzleView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        games = MasterGame.objects.all()
        if not games.exists():
            sample_pgn = (
                "1. e4 d6 2. d4 Nf6 3. Nc3 g6 4. Be3 Bg7 5. Qd2 c6 6. f3 b5 7. Nge2 Nbd7 "
                "8. Bh6 Bxh6 9. Qxh6 Bb7 10. a3 e5 11. O-O-O Qe7 12. Kb1 a6 13. Nc1 O-O-O "
                "14. Nb3 exd4 15. Rxd4 c5 16. Rd1 Nb6 17. g3 Kb8 18. Na5 Ba8 19. Bh3 d5 "
                "20. Qf4+ Ka7 21. Rhe1 d4 22. Nd5 Nbxd5 23. exd5 Qd6 24. Rxd4 cxd4 "
                "25. Re7+ Kb6 26. Qxd4+ Kxa5 27. b4+ Ka4 28. Qc3 Qxd5 29. Ra7 Bb7 "
                "30. Rxb7 Qc4 31. Qxf6 Kxa3 32. Qxa6+ Kxb4 33. c3+ Kxc3 34. Qa1+ Kd2 "
                "35. Qb2+ Kd1 36. Bf1 Rd2 37. Rd7 Rxd7 38. Bxc4 bxc4 39. Qxh8 Rd3 "
                "40. Qa8 c3 41. Qa4+ Ke1 42. f4 f5 43. Kc1 Rd2 44. Qa7 1-0"
            )
            return Response([{
                "id": 1,
                "title": "Kasparov vs. Topalov (Wijk aan Zee 1999)",
                "pgn": sample_pgn,
                "decision_ply": 46,
                "gm_move_san": "Rxd4",
                "game_story": "Kasparov initiates one of the most famous rook sacrifices in chess history."
            }])

        data = []
        for g in games:
            calculated_fen = None
            if g.pgn:
                try:
                    pgn_io = io.StringIO(g.pgn)
                    parsed_game = chess.pgn.read_game(pgn_io)
                    if parsed_game:
                        board = parsed_game.board()
                        ply_counter = 0
                        limit = g.decision_ply if g.decision_ply is not None else 0
                        for move in parsed_game.mainline_moves():
                            if ply_counter >= limit:
                                break
                            board.push(move)
                            ply_counter += 1
                        calculated_fen = board.fen()
                except Exception:
                    calculated_fen = None

            data.append({
                "id": g.id,
                "title": g.title,
                "pgn": g.pgn,
                "decision_ply": g.decision_ply,
                "gm_move_san": g.gm_move_san,
                "gm_idea": g.gm_idea,
                "game_story": g.game_story,
                "fen": calculated_fen
            })
        
        return Response(data)