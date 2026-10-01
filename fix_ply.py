import os
import django
import io
import chess.pgn

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # Replace 'chess_project' with your actual settings folder name if different
django.setup()

from core.models import MasterGame  # Adjust 'core' if your app name is different

def fix_all_decision_plies():
    updated_count = 0
    for game in MasterGame.objects.all():
        if not game.pgn or not game.gm_move_san:
            continue

        target_san = game.gm_move_san.strip().replace('+', '').replace('#', '')
        pgn_io = io.StringIO(game.pgn)
        parsed_game = chess.pgn.read_game(pgn_io)

        if not parsed_game:
            continue

        board = parsed_game.board()
        found_ply = None

        for ply, move in enumerate(parsed_game.mainline_moves()):
            san = board.san(move).replace('+', '').replace('#', '')
            if san == target_san:
                found_ply = ply
                break
            board.push(move)

        if found_ply is not None and found_ply != game.decision_ply:
            print(f"Fixed '{game.title}': ply {game.decision_ply} -> {found_ply}")
            game.decision_ply = found_ply
            game.save()
            updated_count += 1

    print(f"\nDone! Updated {updated_count} game(s).")

if __name__ == '__main__':
    fix_all_decision_plies()