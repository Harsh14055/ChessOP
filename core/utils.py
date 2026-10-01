# core/utils.py
import requests
import chess.pgn
import io
from core.models import Flashcard 
import json
import urllib.request
import io
import chess
import chess.pgn
from core.models import Flashcard
import lichess.api
from lichess.format import PYCHESS
def update_game_elo(white_user, black_user, outcome):
    """
    outcome: 'white_win', 'black_win', or 'draw'
    """
    if not white_user or not black_user:
        return  # Do not update ratings for guest/bot matches

    white_profile = white_user.profile
    black_profile = black_user.profile

    r_w = white_profile.elo_rating
    r_b = black_profile.elo_rating

    # Expected outcome probabilities
    e_w = 1 / (1 + 10 ** ((r_b - r_w) / 400))
    e_b = 1 / (1 + 10 ** ((r_w - r_b) / 400))

    # Actual outcome score
    if outcome == 'white_win':
        s_w, s_b = 1.0, 0.0
    elif outcome == 'black_win':
        s_w, s_b = 0.0, 1.0
    else:  # draw
        s_w, s_b = 0.5, 0.5

    k = 32  # Rating volatility factor
    white_profile.elo_rating = round(r_w + k * (s_w - e_w))
    black_profile.elo_rating = round(r_b + k * (s_b - e_b))

    white_profile.save()
    black_profile.save()
    
 # Adjust model import based on your setup

import io
import time
import requests
import chess
import chess.pgn
from core.models import Flashcard


# Curated Grandmaster Middlegame Positions
REAL_GM_POSITIONS = [
    {
        "title": "Kasparov vs. Topalov (Wijk aan Zee 1999)",
        "fen": "d5r1/4bpk1/p1q1p2p/1p2P1p1/1P2N3/P1P2RPP/5P2/3Q2K1 w - - 1 32",
        "difficulty": "HARD"
    },
    {
        "title": "Carlsen vs. Anand (World Championship 2013)",
        "fen": "8/8/4k3/4p3/2r5/1R3P2/1P1K4/8 b - - 5 45",
        "difficulty": "MEDIUM"
    },
    {
        "title": "Fischer vs. Spassky (Match 1972)",
        "fen": "r1bqk2r/pp3ppp/2n1pn2/2bp4/8/2P1PN2/PP1N1PPP/R1BQKB1R w KQkq - 2 7",
        "difficulty": "EASY"
    },
    {
        "title": "Nakamura vs. Caruana (Candidates 2024)",
        "fen": "2r3k1/pp3p1p/4p1p1/1b1pP3/1P1P1P2/P1r2N2/3R1KPP/R7 w - - 3 24",
        "difficulty": "MEDIUM"
    },
    {
        "title": "Tal vs. Botvinnik (World Championship 1960)",
        "fen": "2rq1rk1/1p1nbppp/p2pbn2/4p3/4P3/1NN1BP2/PPPQB1PP/2KR3R w - - 1 12",
        "difficulty": "HARD"
    },
    {
        "title": "Capablanca vs. Lasker (World Championship 1921)",
        "fen": "r4rk1/pb1n1ppp/1p1qpn2/2pp4/3P4/2PBPN2/PP1N1PPP/R2Q1RK1 w - - 0 11",
        "difficulty": "EASY"
    },
    {
        "title": "Firouzja vs. Ding Liren (Tata Steel 2020)",
        "fen": "r2q1rk1/1b2bppp/p2ppn2/1p6/3BPP2/2N5/PPP1B1PP/R2Q1R1K w - - 0 14",
        "difficulty": "MEDIUM"
    }
]
import os
LICHESS_TOKEN = os.environ.get("LICHESS_TOKEN")


def fetch_gm_positions(count=20):
    gm_usernames = ['DrNykterstein', 'penguingm1', 'RebeccaHarris', 'nihalsarin']
    added_count = 0

    for username in gm_usernames:
        if added_count >= count:
            break

        url = f"https://lichess.org/api/games/user/{username}?max=5&perfType=blitz,rapid,classical&evals=false"
        
        headers = {
            "Accept": "application/x-ndjson",
            "User-Agent": "ChessOP-App/1.0 (contact: email@example.com)"
        }
        if LICHESS_API_TOKEN:
            headers["Authorization"] = f"Bearer {LICHESS_API_TOKEN}"

        req = urllib.request.Request(url, headers=headers)

        try:
            # Respect Lichess rate limits by delaying before each request
            time.sleep(2.0)

            with urllib.request.urlopen(req, timeout=10) as response:
                for line in response:
                    if added_count >= count:
                        break

                    game_data = json.loads(line.decode('utf-8'))
                    moves_str = game_data.get('moves', '')

                    if not moves_str:
                        continue

                    board = chess.Board()
                    moves = moves_str.split()

                    if len(moves) > 20:
                        target_move = min(30, len(moves) - 1)
                        for idx, move_san in enumerate(moves):
                            board.push_san(move_san)
                            if idx == target_move:
                                fen = board.fen()
                                if not Flashcard.objects.filter(fen=fen).exists():
                                    Flashcard.objects.create(
                                        title=f"{username}'s Game Position",
                                        fen=fen,
                                        difficulty='MEDIUM'
                                    )
                                    added_count += 1
                                break

        except urllib.error.HTTPError as e:
            if e.code == 429:
                print(f"Rate limited (429) on {username}. Waiting 60 seconds before next request...")
                time.sleep(60) # Pause for rate limit cooldown
            else:
                print(f"HTTP Error {e.code} for {username}: {e.reason}")
        except Exception as e:
            print(f"Error fetching games for {username}: {e}")

    return added_count