import os
import sys

# Project path configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Django Setup BEFORE model imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from core.models import MasterGame

MASTER_GAMES_DATA = [
    {
        "title": "Kasparov vs. Topalov (Wijk aan Zee 1999)",
        "pgn": "1. e4 d6 2. d4 Nf6 3. Nc3 g6 4. Be3 Bg7 5. Qd2 c6 6. f3 b5 7. Nge2 Nbd7 8. Bh6 Bxh6 9. Qxh6 Bb7 10. a3 e5 11. O-O-O Qe7 12. Kb1 a6 13. Nc1 O-O-O 14. Nb3 exd4 15. Rxd4 c5 16. Rd1 Nb6 17. g3 Kb8 18. Na5 Ba8 19. Bh3 d5 20. Qf4+ Ka7 21. Rhe1 d4 22. Nd5 Nbxd5 23. exd5 Qd6 24. Rxd4 cxd4 25. Re7+ Kb6 26. Qxd4+ Kxa5 27. b4+ Ka4 28. Qc3 Qxd5 29. Ra7 Bb7 30. Rxb7 Qc4 31. Qxf6 Kxa3 32. Qxa6+ Kxb4 33. c3+ Kxc3 34. Qa1+ Kd2 35. Qb2+ Kd1 36. Bf1 Rd2 37. Rd7 Rxd7 38. Bxc4 bxc4 39. Qxh8 Rd3 40. Qa8 c3 41. Qa4+ Ke1 42. f4 f5 43. Kc1 Rd2 44. Qa7 1-0",
        "decision_ply": 46,
        "gm_move_san": "Rxd4",
        "gm_idea": "Kasparov sacrifices the rook on d4 to dismantle Black's pawn cover, initiating a historic king hunt.",
        "game_story": "Celebrated as 'Kasparov's Immortal', played in Round 4 of Wijk aan Zee 1999."
    },
    {
        "title": "Morphy vs. Duke Karl / Count Isouard (Paris Opera 1858)",
        "pgn": "1. e4 e5 2. Nf3 d6 3. d4 Bg4 4. dxe5 Bxf3 5. Qxf3 dxe5 6. Bc4 Nf6 7. Qb3 Qe7 8. Nc3 c6 9. Bg5 b5 10. Nxb5 cxb5 11. Bxb5+ Nbd7 12. O-O-O Rd8 13. Rxd7 Rxd7 14. Rd1 Qe6 15. Bxd7+ Nxd7 16. Qb8+ Nxb8 17. Rd8# 1-0",
        "decision_ply": 30,
        "gm_move_san": "Qb8+",
        "gm_idea": "Morphy deflects the d7 knight with a queen sacrifice, enabling a back-rank rook checkmate.",
        "game_story": "Played in a private box during an opera performance in Paris, demonstrating classical development principles."
    },
    {
        "title": "Byrne vs. Fischer (New York 1956)",
        "pgn": "1. Nf3 Nf6 2. c4 g6 3. Nc3 Bg7 4. d4 O-O 5. Bf4 d5 6. Qb3 dxc4 7. Qxc4 c6 8. e4 Nbd7 9. Rd1 Nb6 10. Qc5 Bg4 11. Bg5 Na4 12. Qa3 Nxc3 13. bxc3 Nxe4 14. Bxe7 Qb6 15. Bc4 Nxc3 16. Bc5 Rfe8+ 17. Kf1 Be6 18. Bxb6 Bxc4+ 19. Kg1 Ne2+ 20. Kf1 Nxd4+ 21. Kg1 Ne2+ 22. Kf1 Nc3+ 23. Kg1 axb6 24. Qb4 Ra4 25. Qxb6 Nxd1 0-1",
        "decision_ply": 33,
        "gm_move_san": "Be6",
        "gm_idea": "A 13-year-old Fischer offers his queen to setup a crushing windmill attack with minor pieces.",
        "game_story": "Dubbed 'The Game of the Century' after Fischer defeated International Master Donald Byrne."
    },
    {
        "title": "Rotlewi vs. Rubinstein (Lodz 1907)",
        "pgn": "1. d4 d5 2. Nf3 e6 3. e3 c5 4. c4 Nc6 5. Nc3 Nf6 6. dxc5 Bxc5 7. a3 a6 8. b4 Bd6 9. Bb2 O-O 10. Qd2 Qe7 11. Bd3 dxc4 12. Bxc4 b5 13. Bd3 Rd8 14. Qe2 Bb7 15. O-O Ne5 16. Nxe5 Bxe5 17. f4 Bc7 18. e4 Rac8 19. e5 Bb6+ 20. Kh1 Ng4 21. Be4 Qh4 22. g3 Rxc3 23. gxh4 Rd2 24. Qxd2 Bxe4+ 25. Qg2 Rh3 0-1",
        "decision_ply": 43,
        "gm_move_san": "Rxc3",
        "gm_idea": "Rubinstein sacrifices his queen to unleash his active bishop pair and remaining rook in an unavoidable mating sequence.",
        "game_story": "Known as 'Rubinstein's Immortal', showcasing ideal piece harmony and tactical coordination."
    },
    {
        "title": "Anderssen vs. Kieseritzky (London 1851)",
        "pgn": "1. e4 e5 2. f4 exf4 3. Bc4 Qh4+ 4. Kf1 b5 5. Bxb5 Nf6 6. Nf3 Qh6 7. d3 Nh5 8. Nh4 Qg5 9. Nf5 c6 10. g4 Nf6 11. Rg1 cxb5 12. h4 Qg6 13. h5 Qg5 14. Qf3 Ng8 15. Bxf4 Qf6 16. Nc3 Bc5 17. Nd5 Qxb2 18. Bd6 Bxg1 19. e5 Qxa1+ 20. Ke2 Na6 21. Nxg7+ Kd8 22. Qf6+ Nxf6 23. Be7# 1-0",
        "decision_ply": 36,
        "gm_move_san": "e5",
        "gm_idea": "Anderssen sacrifices both rooks and a bishop to isolate Black's queen and force mate with minor pieces.",
        "game_story": "Titled 'The Immortal Game', played during the first major international tournament in London 1851."
    },
    {
        "title": "Ivanchuk vs. Yusupov (Brussels 1991)",
        "pgn": "1. c4 e5 2. g3 d6 3. Bg2 g6 4. d4 Nbd7 5. Nc3 Bg7 6. Nf3 Ngf6 7. O-O O-O 8. Qc2 Re8 9. Rd1 c6 10. b3 Qe7 11. Ba3 e4 12. Ng5 e3 13. f4 Nf8 14. b4 Bf5 15. Qb3 h6 16. Nf3 Ne4 17. Nxe4 Bxe4 18. b5 g5 19. fxg5 hxg5 20. Ne5 Bxg2 21. Kxg2 c5 22. Nf3 g4 23. Nh4 Qe4+ 24. Kg1 Ng6 25. Nxg6 fxg6 26. Bb2 Rf8 27. Rf1 Rf2 28. Rxf2 exf2+ 29. Kxf2 Rf8+ 0-1",
        "decision_ply": 53,
        "gm_move_san": "Rf2",
        "gm_idea": "Yusupov penetrates the 2nd rank with a rook sacrifice on f2 to crush White's king position.",
        "game_story": "A dramatic match-winner from the 1991 Candidates Tournament in Brussels."
    },
    {
        "title": "Karpov vs. Kasparov (World Championship 1985, Game 16)",
        "pgn": "1. e4 c5 2. Nf3 e6 3. d4 cxd4 4. Nxd4 Nc6 5. Nb5 d6 6. c4 Nf6 7. N1c3 a6 8. Na3 d5 9. cxd5 exd5 10. exd5 Nb4 11. Be2 Bc5 12. O-O O-O 13. Bf3 Bf5 14. Bg5 Re8 15. Qd2 b5 16. Rad1 Nd3 17. Nab1 h6 18. Bh4 b4 19. Na4 Bd6 20. Bg3 Rc8 21. b3 g5 22. Bxd6 Qxd6 23. g3 Nd7 24. Bg2 Qf6 25. a3 a5 26. axb4 axb4 27. Qa2 Qa6 28. d6 g4 29. Qd2 Kg7 30. f3 Qxd6 31. fxg4 Qd4+ 32. Kh1 Bg6 33. Rf4 Qe3 0-1",
        "decision_ply": 31,
        "gm_move_san": "Nd3",
        "gm_idea": "Kasparov plants a knight on d3 that completely paralyzes White's army.",
        "game_story": "Features Kasparov's famous 'octopus knight' that helped him secure the 1985 World Championship."
    },
    {
        "title": "Short vs. Timman (Tilburg 1991)",
        "pgn": "1. e4 Nf6 2. e5 Nd5 3. d4 d6 4. Nf3 g6 5. Bc4 Nb6 6. Bb3 Bg7 7. Qe2 Nc6 8. O-O O-O 9. h3 a5 10. a4 dxe5 11. dxe5 Nd4 12. Nxd4 Qxd4 13. Re1 e6 14. Nd2 Nd5 15. Nf3 Qc5 16. Qe4 Qb4 17. Bc4 Nb6 18. b3 Nxc4 19. bxc4 Re8 20. Rd1 Qc5 21. Qh4 b6 22. Be3 Qc6 23. Bh6 Bh8 24. Rd8 Bb7 25. Rad1 Bg7 26. Bxg7 Kxg7 27. R1d4 Rexd8 28. Qf6+ Kg8 29. Rxd8+ Rxd8 30. Qxd8+ Kg7 31. Kh2 Qc5 32. Kg3 Qc6 33. Kh4 h6 34. Kf5 1-0",
        "decision_ply": 65,
        "gm_move_san": "Kh4",
        "gm_idea": "Nigel Short walks his king all the way to h6 while heavy pieces are still on the board to construct a mating net.",
        "game_story": "One of the most remarkable king marches in top-level chess history."
    },
    {
        "title": "Tal vs. Smyslov (Bled Candidates 1959)",
        "pgn": "1. e4 c6 2. d3 d5 3. Nd2 e5 4. Ngf3 Nd7 5. d4 dxe4 6. Nxe4 exd4 7. Qxd4 Ngf6 8. Bg5 Be7 9. O-O-O O-O 10. Nd6 Qa5 11. Bc4 b5 12. Bd2 Qa6 13. Nf5 Bd8 14. Qh4 bxc4 15. Qg5 Nh5 16. Nh6+ Kh8 17. Qxh5 Qxa2 18. Bc3 Nf6 19. Qxf7 Qa1+ 20. Kd2 Rxf7 21. Nxf7+ Kg8 22. Rxa1 Kxf7 1-0",
        "decision_ply": 28,
        "gm_move_san": "Qxf7",
        "gm_idea": "Tal sacrifices his queen to trigger a forcing sequence that dismantles Black's back rank.",
        "game_story": "Demonstrates Mikhail Tal's relentless tactical aggression during the 1959 Candidates Tournament."
    },
    {
        "title": "Capablanca vs. Tartakower (New York 1924)",
        "pgn": "1. d4 e6 2. Nf3 f5 3. c4 Nf6 4. Bg5 Be7 5. e3 O-O 6. Nc3 b6 7. Bd3 Bb7 8. O-O Qe8 9. Qe2 Ne4 10. Bxe7 Nxc3 11. bxc3 Qxe7 12. a4 Bxf3 13. Qxf3 Nc6 14. e4 fxe4 15. Qxe4 g6 16. Rae1 Qf6 17. Re3 Rf7 18. Rf3 Qg7 19. Rxf7 Qxf7 20. Re1 Rf8 21. f3 Qf4 22. Qxf4 Rxf4 23. Be4 Na5 24. c5 bxc5 25. dxc5 Kf8 26. Rd1 Ke7 27. Rd4 Rf8 28. Rb4 Nb3 29. Rb7 Nd2 30. Bd3 1-0",
        "decision_ply": 50,
        "gm_move_san": "c5",
        "gm_idea": "Capablanca creates an active rook endgame by advancing his king and pawns with surgical technique.",
        "game_story": "Widely regarded as one of the textbook examples of endgame mastery by José Raúl Capablanca."
    }
]

def seed_database():
    MasterGame.objects.all().delete()
    print("Cleared existing master games from database.")

    for idx, item in enumerate(MASTER_GAMES_DATA, 1):
        MasterGame.objects.create(**item)
        print(f"[{idx}/{len(MASTER_GAMES_DATA)}] Seeded: {item['title']}")

    print(f"\nSuccessfully populated {len(MASTER_GAMES_DATA)} Master Games into the database!")

if __name__ == '__main__':
    seed_database()