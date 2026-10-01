import json
import chess
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Game
from .utils import update_game_elo

class ChessGameConsumer(AsyncWebsocketConsumer):
    room_roles = {}
    room_connections = {}
    room_scores = {}

    async def connect(self):
        self.room_code = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = f'game_{self.room_code}'
        self.user = self.scope.get('user', None)

        if self.room_code not in type(self).room_roles:
            type(self).room_roles[self.room_code] = {'white': None, 'black': None}
        if self.room_code not in type(self).room_connections:
            type(self).room_connections[self.room_code] = set()

        type(self).room_connections[self.room_code].add(self.channel_name)

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        role_info = await self.assign_or_get_db_role()
        self.role = role_info['role']

        await self.initialize_or_update_scores()
        scores = await self.get_formatted_scores()

        # Broadcast update to room so opponent sees names update immediately
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'player_joined_event',
                'scores': scores,
                'white_username': role_info.get('white_username'),
                'black_username': role_info.get('black_username')
            }
        )

        await self.send(text_data=json.dumps({
            'type': 'role_assignment',
            'role': self.role,
            'channel_name': self.channel_name,
            'white_rating': role_info.get('white_rating'),
            'black_rating': role_info.get('black_rating'),
            'scores': scores
        }))

    async def disconnect(self, close_code):
        # 1. Clear player slot in DB first before dropping connections
        await self.handle_player_departure_db()

        if self.room_code in type(self).room_connections:
            type(self).room_connections[self.room_code].discard(self.channel_name)
            
            # If room is completely empty of active connections, wipe it from DB & memory
            if len(type(self).room_connections[self.room_code]) == 0:
                type(self).room_connections.pop(self.room_code, None)
                type(self).room_roles.pop(self.room_code, None)
                type(self).room_scores.pop(self.room_code, None)
                await self.delete_room_from_db()
            else:
                # Otherwise, notify remaining players someone left
                scores = await self.get_formatted_scores()
                username = self.user.username if (self.user and self.user.is_authenticated) else "A player"
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'player_left',
                        'sender_channel': self.channel_name,
                        'username': username,
                        'scores': scores
                    }
                )

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    @database_sync_to_async
    def initialize_or_update_scores(self):
        try:
            game = Game.objects.get(room_code=self.room_code)
        except Game.DoesNotExist:
            return

        p1_name = game.white_player.username if game.white_player else "Waiting..."
        p2_name = game.black_player.username if game.black_player else "Waiting..."

        if self.room_code not in type(self).room_scores:
            type(self).room_scores[self.room_code] = {
                'player1': p1_name,
                'player2': p2_name,
                'p1_wins': 0,
                'p2_wins': 0,
                'draw': 0
            }
        else:
            type(self).room_scores[self.room_code]['player1'] = p1_name
            type(self).room_scores[self.room_code]['player2'] = p2_name

    @database_sync_to_async
    def get_game_obj_safely(self):
        try:
            game = Game.objects.get(room_code=self.room_code)
            return {
                'white_username': game.white_player.username if game.white_player else None,
                'black_username': game.black_player.username if game.black_player else None
            }
        except Game.DoesNotExist:
            return None

    async def get_formatted_scores(self):
        await self.initialize_or_update_scores()
        return type(self).room_scores.get(self.room_code, {
            'player1': 'Player 1',
            'player2': 'Player 2',
            'p1_wins': 0,
            'p2_wins': 0,
            'draw': 0
        })

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'get_state':
            result = await self.get_game_state()
            if result:
                role_info = await self.assign_or_get_db_role()
                self.role = role_info['role']
                scores = await self.get_formatted_scores()

                await self.send(text_data=json.dumps({
                    'type': 'role_assignment',
                    'role': self.role,
                    'channel_name': self.channel_name,
                    'white_rating': role_info.get('white_rating'),
                    'black_rating': role_info.get('black_rating')
                }))

                await self.send(text_data=json.dumps({
                    'type': 'game_state',
                    'fen': result['fen'],
                    'status': result['status'],
                    'winner': result['winner'],
                    'turn': result['turn'],
                    'is_checkmate': result['is_checkmate'],
                    'is_draw': result['is_draw'],
                    'moves': result['moves'],
                    'scores': scores
                }))
        elif action == 'chat_message':
            message = data.get('message', '').strip()
            if message:
                sender_name = self.user.username if (self.user and self.user.is_authenticated) else "Spectator"
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message_event',
                        'sender': sender_name,
                        'message': message
                    }
                )
        elif action == 'make_move':
            move_san = data.get('move')
            result = await self.process_move(move_san, self.user)

            if result['valid']:
                scores = await self.get_formatted_scores()
                if result['winner']:
                    game_usernames = await self.get_game_obj_safely()
                    if result['winner'] == 'white':
                        if game_usernames and game_usernames['white_username'] == scores['player1']:
                            scores['p1_wins'] += 1
                        else:
                            scores['p2_wins'] += 1
                    elif result['winner'] == 'black':
                        if game_usernames and game_usernames['black_username'] == scores['player2']:
                            scores['p2_wins'] += 1
                        else:
                            scores['p1_wins'] += 1
                    elif result['winner'] == 'draw':
                        scores['draw'] += 1

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_move',
                        'fen': result['fen'],
                        'turn': result['turn'],
                        'move_san': result['move_san'],
                        'move_color': result['move_color'],
                        'is_checkmate': result['is_checkmate'],
                        'is_draw': result['is_draw'],
                        'winner': result['winner'],
                        'scores': scores
                    }
                )
            else:
                await self.send(text_data=json.dumps({
                    'error': result.get('error', 'Invalid move')
                }))

        elif action == 'offer_draw':
            is_active = await self.is_game_active()
            if not is_active:
                await self.send(text_data=json.dumps({
                    'error': 'Cannot offer a draw. The game is already over.'
                }))
            else:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'draw_offered',
                        'sender': self.user.username if (self.user and self.user.is_authenticated) else "Opponent",
                        'sender_channel': self.channel_name
                    }
                )

        elif action == 'accept_draw':
            result = await self.process_draw_acceptance()
            if result['valid']:
                scores = await self.get_formatted_scores()
                scores['draw'] += 1
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_over',
                        'reason': 'draw_agreed',
                        'winner': 'draw',
                        'scores': scores
                    }
                )

        elif action == 'decline_draw':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'draw_declined',
                    'sender': self.user.username if (self.user and self.user.is_authenticated) else "Opponent",
                    'sender_channel': self.channel_name
                }
            )

        elif action == 'resign':
            result = await self.process_resignation(self.user)
            if result['valid']:
                scores = await self.get_formatted_scores()
                winner = result['winner']
                game_usernames = await self.get_game_obj_safely()
                
                if winner == 'white':
                    if game_usernames and game_usernames['white_username'] == scores['player1']:
                        scores['p1_wins'] += 1
                    else:
                        scores['p2_wins'] += 1
                elif winner == 'black':
                    if game_usernames and game_usernames['black_username'] == scores['player2']:
                        scores['p2_wins'] += 1
                    else:
                        scores['p1_wins'] += 1

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_over',
                        'reason': 'resignation',
                        'winner': winner,
                        'scores': scores
                    }
                )
            else:
                await self.send(text_data=json.dumps({
                    'error': result.get('error', 'Could not resign')
                }))

        elif action == 'reset_game':
            result = await self.reset_game_state()
            if result['valid']:
                role = await self.get_current_user_role()
                scores = await self.get_formatted_scores()
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_reset',
                        'fen': result['fen'],
                        'turn': result['turn'],
                        'new_role': role,
                        'scores': scores
                    }
                )

        elif action == 'leave_room':
            await self.handle_leave_room()

    async def handle_leave_room(self):
        username = self.user.username if (self.user and self.user.is_authenticated) else "A player"
        
        try:
            game = await database_sync_to_async(Game.objects.get)(room_code=self.room_code)
            
            if self.user and self.user.is_authenticated:
                if self.user == game.white_player:
                    game.white_player = None
                elif self.user == game.black_player:
                    game.black_player = None
            
            game.status = 'WAITING'
            game.winner = None
            await database_sync_to_async(game.save)()

            if self.room_code in type(self).room_scores:
                if username == type(self).room_scores[self.room_code]['player1']:
                    type(self).room_scores[self.room_code]['player1'] = "Waiting..."
                if username == type(self).room_scores[self.room_code]['player2']:
                    type(self).room_scores[self.room_code]['player2'] = "Waiting..."
        except Game.DoesNotExist:
            pass

        scores = await self.get_formatted_scores()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'player_left',
                'sender_channel': self.channel_name,
                'username': username,
                'scores': scores
            }
        )

    # Event Handlers
    async def chat_message_event(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'sender': event['sender'],
            'message': event['message']
        }))

    async def game_move(self, event):
        await self.send(text_data=json.dumps(event))

    async def game_over(self, event):
        await self.send(text_data=json.dumps(event))

    async def draw_offered(self, event):
        await self.send(text_data=json.dumps(event))

    async def draw_declined(self, event):
        await self.send(text_data=json.dumps(event))

    async def game_reset(self, event):
        role = await self.get_current_user_role()
        data = event.copy()
        data['new_role'] = role
        await self.send(text_data=json.dumps(data))

    async def player_joined_event(self, event):
        scores = await self.get_formatted_scores()
        await self.send(text_data=json.dumps({
            'type': 'player_joined',
            'scores': scores
        }))

    async def player_left(self, event):
        await self.send(text_data=json.dumps({
            'type': 'player_left',
            'sender_channel': event['sender_channel'],
            'username': event['username'],
            'scores': event.get('scores')
        }))

    # DB Operations
    @database_sync_to_async
    def delete_room_from_db(self):
        try:
            Game.objects.filter(room_code=self.room_code).delete()
        except Exception:
            pass

    @database_sync_to_async
    def assign_or_get_db_role(self):
        try:
            game, created = Game.objects.get_or_create(room_code=self.room_code, defaults={
                'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
                'status': 'WAITING'
            })
            user = self.user if (self.user and self.user.is_authenticated) else None

            role = 'spectator'
            if user:
                if game.white_player == user:
                    role = 'white'
                elif game.black_player == user:
                    role = 'black'
                elif game.white_player is None:
                    game.white_player = user
                    game.status = 'WAITING'
                    game.save()
                    role = 'white'
                elif game.black_player is None and game.white_player != user:
                    game.black_player = user
                    game.status = 'IN_PROGRESS'
                    game.save()
                    role = 'black'

            white_rating = getattr(game.white_player, 'rating', 1200) if game.white_player else 1200
            black_rating = getattr(game.black_player, 'rating', 1200) if game.black_player else 1200

            return {
                'role': role,
                'white_rating': white_rating,
                'black_rating': black_rating,
                'white_username': game.white_player.username if game.white_player else None,
                'black_username': game.black_player.username if game.black_player else None,
            }
        except Exception:
            return {'role': 'spectator', 'white_rating': 1200, 'black_rating': 1200, 'white_username': None, 'black_username': None}

    @database_sync_to_async
    def get_current_user_role(self):
        try:
            game = Game.objects.get(room_code=self.room_code)
            if self.user and self.user.is_authenticated:
                if self.user == game.white_player:
                    return 'white'
                elif self.user == game.black_player:
                    return 'black'
            return 'spectator'
        except Game.DoesNotExist:
            return 'spectator'

    @database_sync_to_async
    def get_game_state(self):
        try:
            game, created = Game.objects.get_or_create(room_code=self.room_code, defaults={
                'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
                'status': 'IN_PROGRESS'
            })
            board = chess.Board(game.fen)
            moves_list = getattr(game, 'moves_list', [])

            return {
                'fen': game.fen,
                'status': game.status,
                'winner': game.winner,
                'turn': 'white' if board.turn == chess.WHITE else 'black',
                'is_checkmate': board.is_checkmate(),
                'is_draw': board.is_game_over() and not board.is_checkmate(),
                'white_player': game.white_player.username if game.white_player else None,
                'black_player': game.black_player.username if game.black_player else None,
                'moves': moves_list or []
            }
        except Exception:
            return None

    @database_sync_to_async
    def process_move(self, move_san, user):
        try:
            game = Game.objects.get(room_code=self.room_code)
            if game.status == 'COMPLETED':
                return {'valid': False, 'error': 'Game is already finished.'}

            board = chess.Board(game.fen)
            move_color = 'w' if board.turn == chess.WHITE else 'b'

            if board.turn == chess.WHITE and game.white_player and game.white_player != user:
                return {'valid': False, 'error': "It's White's turn!"}
            if board.turn == chess.BLACK and game.black_player and game.black_player != user:
                return {'valid': False, 'error': "It's Black's turn!"}

            try:
                move = chess.Move.from_uci(move_san)
            except ValueError:
                move = board.parse_san(move_san)

            if move not in board.legal_moves:
                return {'valid': False, 'error': 'Illegal move.'}

            executed_san = board.san(move)
            board.push(move)
            game.fen = board.fen()

            if hasattr(game, 'moves_list') and isinstance(game.moves_list, list):
                game.moves_list.append(executed_san)

            winner = None
            if board.is_checkmate():
                game.status = 'COMPLETED'
                winner = 'white' if board.turn == chess.BLACK else 'black'
                game.winner = winner
                game.save()
                if game.white_player and game.black_player:
                    outcome = 'white_win' if winner == 'white' else 'black_win'
                    update_game_elo(game.white_player, game.black_player, outcome)
            elif board.is_game_over():
                game.status = 'COMPLETED'
                game.winner = 'draw'
                winner = 'draw'

            game.save()

            return {
                'valid': True,
                'fen': game.fen,
                'turn': 'white' if board.turn == chess.WHITE else 'black',
                'move_san': executed_san,
                'move_color': move_color,
                'is_checkmate': board.is_checkmate(),
                'is_draw': board.is_game_over() and not board.is_checkmate(),
                'winner': winner
            }
        except Exception as e:
            return {'valid': False, 'error': str(e)}

    @database_sync_to_async
    def is_game_active(self):
        try:
            game = Game.objects.get(room_code=self.room_code)
            return game.status != 'COMPLETED'
        except Game.DoesNotExist:
            return False

    @database_sync_to_async
    def process_resignation(self, user):
        try:
            game = Game.objects.get(room_code=self.room_code)
            if game.status == 'COMPLETED':
                return {'valid': False, 'error': 'Game is already finished.'}

            if user == game.white_player:
                winner = 'black'
            elif user == game.black_player:
                winner = 'white'
            else:
                return {'valid': False, 'error': 'Spectators cannot resign.'}

            game.status = 'COMPLETED'
            game.winner = winner
            game.save()
            return {'valid': True, 'winner': winner}
        except Exception as e:
            return {'valid': False, 'error': str(e)}

    @database_sync_to_async
    def process_draw_acceptance(self):
        try:
            game = Game.objects.get(room_code=self.room_code)
            if game.status == 'COMPLETED':
                return {'valid': False, 'error': 'Game is already finished.'}

            game.status = 'COMPLETED'
            game.winner = 'draw'
            game.save()
            return {'valid': True}
        except Exception as e:
            return {'valid': False, 'error': str(e)}

    @database_sync_to_async
    def reset_game_state(self):
        try:
            game = Game.objects.get(room_code=self.room_code)
            game.white_player, game.black_player = game.black_player, game.white_player
            starting_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
            game.fen = starting_fen
            game.status = 'IN_PROGRESS'
            game.winner = None
            if hasattr(game, 'moves_list'):
                game.moves_list = []
            game.save()
            return {'valid': True, 'fen': starting_fen, 'turn': 'white'}
        except Exception as e:
            return {'valid': False, 'error': str(e)}