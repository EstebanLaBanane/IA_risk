#! /bin/python3
import os
import sys
import random
from multiprocessing import Pool, cpu_count
from model.world import World
from model.state_informations import undefeated_armies
from boards.classic_board import risk_map
from ais.neutrals import strategy_neutral_fully_random, strategy_neutral_uniform_random
from ais.randoms import strategy_fully_random,strategy_uniform_random

from ais.probabilistics import strategy_safe,strategy_UCB

from game.game import game
from game.setup import random_initial_state

# --- CONFIG ------------------------------------------------------------
R_MAX = 500
N_GAMES = 500
GAME = [4,3,1,2]
# ----------------------------------------------------------------------

AIs = {
    -2: strategy_neutral_fully_random,
    -1: strategy_neutral_uniform_random,
    1: strategy_fully_random,
    2: strategy_uniform_random,
    3: strategy_safe,
    4: strategy_UCB,
}

# --- SINGLE GAME FUNCTION ---------------------------------------------
def play_one(_):
    """Joue une partie complète et renvoie le nom du vainqueur."""
    lineup = random.sample(GAME, k=len(GAME))
    lineup_strategies = [AIs[j] for j in lineup]
    world = World(lineup_strategies, *risk_map())

    s0 = random_initial_state(world)
    P = game(s0, R_MAX)
    sf = s0 if len(P) == 0 else P[-1][1]
    winners = list(undefeated_armies(sf))

    if len(winners) == 1:
        return winners[0].strategy.name
    else:
        return "draw"

# --- MAIN --------------------------------------------------------------
if __name__ == "__main__":
    if sys.platform == "win32":
        os.system("")  # enable color

    print(f"=== PolyRisk batch ===\nGames: {N_GAMES}\nLineup: {GAME}\nR_MAX: {R_MAX}\n")

    n_cpu = min(cpu_count(), 12)  # limite à 12 threads pour éviter surcharge
    print(f"→ Using {n_cpu} CPU cores")

    with Pool(processes=n_cpu) as pool:
        results = list(pool.imap_unordered(play_one, range(N_GAMES)))

    # --- AGGREGATE RESULTS ---
    wins = {}
    for w in results:
        wins[w] = wins.get(w, 0) + 1

    print("\n--- Final results ---")
    total = sum(wins.values())
    for k, v in sorted(wins.items(), key=lambda x: x[1], reverse=True):
        pct = 100 * v / total
        print(f"{k:40s}: {v:4d} wins ({pct:5.1f}%)")
