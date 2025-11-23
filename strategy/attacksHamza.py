from typing import Tuple, Optional
from random import choice, random
import math

from probabilities_single_battle import (
    all_battles_11, all_battles_12,
    all_battles_21, all_battles_22,
    all_battles_31, all_battles_32
)

from model.region import Unit
from model.army import Army
from model.territory import Territory
from model.state import State
from model.state_informations import (
    territory_occupant,
    territory_units,
    is_defeated_army,
    army_territory_fronts,
)


battle_outcomes = {
    (1,1): all_battles_11(),
    (1,2): all_battles_12(),
    (2,1): all_battles_21(),
    (2,2): all_battles_22(),
    (3,1): all_battles_31(),
    (3,2): all_battles_32(),
}

battle_outcomes = {
    key: [(pa, pd, p) for (pa, pd), p in hist.items()]
    for key, hist in battle_outcomes.items()
}

def sample_from_outcomes(outcomes):
    r = random()
    acc = 0.0
    for pa, pd, p in outcomes:
        acc += p
        if r <= acc:
            return pa, pd
    return outcomes[-1][0], outcomes[-1][1]


def simulate_full_assault(a, d):
    while a > 1 and d > 0:
        att_dice = min(3, a - 1)
        def_dice = min(2, d)
        pa, pd = sample_from_outcomes(battle_outcomes[(att_dice, def_dice)])
        a -= pa
        d -= pd
    return 1 if d <= 0 else 0


def compute_attacker_win_prob(max_attacker_units: int,
                              max_defender_units: int) -> dict:

    from functools import lru_cache

    @lru_cache(maxsize=None)
    def P(a: int, d: int) -> float:
        if d <= 0:
            return 1.0
        if a <= 1:
            return 0.0

        def_dice = min(2, d)
        best = 0.0
        max_att_dice = min(3, a - 1)

        for att_dice in range(1, max_att_dice + 1):
            key = (att_dice, def_dice)
            if key not in battle_outcomes:
                continue
            sprob = 0.0
            for (pa, pd, prob) in battle_outcomes[key]:
                na = max(0, a - pa)
                nd = max(0, d - pd)
                sprob += prob * P(na, nd)
            best = max(best, sprob)

        return best

    return P

def safe_attack(s: State,
                a: Army,
                threshold: float = 0.858
                ) -> Optional[Tuple[Territory, Territory, Unit]]:

    assert a in s.world.armies and not is_defeated_army(s, a)

    candidates = [
        (t_a, t_d, n)
        for (t_a, t_d) in s.world.adjacencies
        if territory_occupant(s, t_a) == a
        if territory_occupant(s, t_d) != a
        if (u_a := territory_units(s, t_a)) > 1
        for n in range(1, min(3, u_a - 1) + 1)
    ]
    if not candidates:
        return None

    max_a = max(territory_units(s, t_a) for (t_a, _, _) in candidates)
    max_d = max(territory_units(s, t_d) for (_, t_d, _) in candidates)
    P = compute_attacker_win_prob(max_a, max_d)

    best, best_prob = None, -1.0

    for (t_a, t_d, n) in candidates:
        prob = P(territory_units(s, t_a), territory_units(s, t_d))
        if prob >= threshold and prob > best_prob:
            best, best_prob = (t_a, t_d, n), prob

    return best

class Node:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.visits = 0
        self.value = 0.0
        self.children = []

    def ucb1(self, c=1.4):
        if self.visits == 0:
            return float('inf')
        return (
            self.value / self.visits +
            c * math.sqrt(math.log(self.parent.visits + 1) / self.visits)
        )

def _can_complete_region_by_conquest(s: State, attacker: Army, target: Territory) -> bool:
    from model.state_informations import territory_occupant
    region = target.region
    region_terrs = s.world.region_territories[region]
    for t in region_terrs:
        if t != target and territory_occupant(s, t) != attacker:
            return False
    return True

def UCB_attack(
    s: State,
    a: Army,
    iterations: int = 100,
    threshold: float = 0.83,
) -> Optional[Tuple[Territory, Territory, Unit]]:

    assert a in s.world.armies and not is_defeated_army(s, a)

    # Generate attack candidates
    candidates = [
        (t_a, t_d, min(3, territory_units(s, t_a) - 1))
        for (t_a, t_d) in s.world.adjacencies
        if territory_occupant(s, t_a) == a
        if territory_occupant(s, t_d) != a
        if territory_units(s, t_a) > 1
    ]
    if not candidates:
        return None

    root = Node(s)

    # Create child nodes
    for (t_a, t_d, n) in candidates:
        a_u = territory_units(s, t_a)
        d_u = territory_units(s, t_d)
        root.children.append(Node(state=(a_u, d_u), parent=root, action=(t_a, t_d, n)))

    # MCTS iterations (full assault only)
    for _ in range(iterations):
        node = max(root.children, key=lambda n: n.ucb1())
        a_units, d_units = node.state

        outcome = simulate_full_assault(a_units, d_units)

        node.visits += 1
        node.value += outcome
        root.visits += 1
        root.value += outcome

    # Selection phase
    REGION_BONUS = 0.33
    MIN_THRESHOLD = 0.5

    best_child = None
    best_score = -1.0

    for child in root.children:
        avg_win = child.value / max(1, child.visits)
        (_, t_d, _) = child.action

        # threshold adjustment
        local_threshold = (
            max(MIN_THRESHOLD, threshold - REGION_BONUS)
            if _can_complete_region_by_conquest(s, a, t_d)
            else threshold
        )

        if avg_win >= local_threshold and avg_win > best_score:
            best_child = child
            best_score = avg_win

    return None if best_child is None else best_child.action
