from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Game, MasterGame, FlashcardPosition

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'rating', 'guess_the_move_score', 'board_vision_accuracy', 'created_at']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        # Automatically create the corresponding UserProfile
        UserProfile.objects.create(user=user)
        return user

class GameSerializer(serializers.ModelSerializer):
    white_username = serializers.CharField(source='white_player.username', read_only=True)
    black_username = serializers.CharField(source='black_player.username', read_only=True)

    class Meta:
        model = Game
        fields = ['id', 'room_code', 'white_player', 'black_player', 'white_username', 'black_username', 'fen', 'status', 'winner', 'created_at']
        read_only_fields = ['room_code', 'fen', 'pgn', 'status', 'winner', 'created_at']

class FlashcardPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlashcardPosition
        fields = ['id', 'title', 'fen', 'difficulty', 'display_duration_seconds']