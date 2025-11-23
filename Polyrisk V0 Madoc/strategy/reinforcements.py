#! /bin/python
# gvim: set fileencoding=utf-8
#
# (c) September 1, 2025, José Martinez, Polytech Nantes, University of Nantes
#
# Licence:  proprietary
# The use of this library is not authorised outside the Polytechnic School of the University of Nantes.
#


"""
Several strategies are provided in order to reinforce an army.

Notice that the pre- and post-conditions of these functions would not need to be tested.
They are already ensured by the strategies.
However, they are repeated to the programmer for clarity and documentation.
Also, this allows to detect a possible flaw closer to its source.
A model is given below.
Notice that post-conditions can be strengthen.

def model_of_reinforcement_function (s: State,
                                     a: Army) -> Dict[Territory, Unit]:
    '''
    :parameter s:  a current state
    :parameter a:  an army to reinforce

    :pre:  The army belongs to the state
    :pre:  The army must not be defeated
    :pre:  The reinforcement units has to be strictly positive (normally, redundant with the previous one)

    :post:  The selected territories belong to the army
    :post:  Each selected territory must receive at least one unit
    :post:  The sum of all the reinforcement units must be equal to `reinforcement_units(s, a)`
    '''
    # PRE-CONDITION
    assert isinstance(s, State)
    assert isinstance(a, Army)
    assert a in s.world.armies, "unknown army to reinforce"
    assert not is_defeated_army(s, a), "defeated army cannot be reinforced"
    assert reinforcement_units(s, a) > 0, "reinforcement units have to be strictly positive"

    result = DO_SOME_STUFF

    # POST-CONDITION
    assert all(territory_occupant(s, t) == a for t in result), "The selected territories belong to the army"
    assert all(result[t] > 0 for t in result), "Each selected territory must receive at least one unit"
    assert sum(result[t] for t in result) == reinforcement_units(s, a), "The sum of all the reinforcement units must be equal to {reinforcement_units(s, a)}"

    return result
"""


__all__ = [
    'random_reinforcement',
    'random_uniform_reinforcement',
    ]


from typing import Dict
from random import shuffle, randint, sample, choice
from model.region import Unit
from model.territory import Territory
from model.state import State
from model.army import Army
from model.state_informations import is_defeated_army, territories_occupied_by_army, reinforcement_units, territory_occupant


def random_reinforcement (s: State,
                          a: Army) -> Dict[Territory, Unit]:
    """
    A random sub-set of the territories receives a random number of units.
    """
    assert isinstance(s, State)
    assert isinstance(a, Army)
    assert a in s.world.armies, "unknown army to reinforce"
    assert not is_defeated_army(s, a), "defeated army cannot be reinforced"
    assert reinforcement_units(s, a) > 0, "reinforcement units have to be strictly positive"

    T_a = territories_occupied_by_army(s, a)
    card_T_a = len(T_a)
    k = randint(1, min(reinforcement_units(s, a), card_T_a)) # type: Unit
    (q, r) = divmod(reinforcement_units(s, a), k)
    result = { t: q
               for t in sample(list(T_a), k) }
    for _ in range(r):
        result[choice(list(result))] += 1

    assert all(territory_occupant(s, t) == a for t in result), "The selected territories belong to the army"
    assert all(result[t] > 0 for t in result), "Each selected territory must receive at least one unit"
    assert sum(result[t] for t in result) == reinforcement_units(s, a), "The sum of all the reinforcement units must be equal to {reinforcement_units(s, a)}"

    return result


def random_uniform_reinforcement (s: State,
                                  a: Army) -> Dict[Territory, Unit]:
    """
    The new units are as evenly as possible distributed over the territories, plus a random distribution of bonuses.

    :post:  uniform distribution of the units
    """
    assert isinstance(s, State)
    assert isinstance(a, Army)
    assert a in s.world.armies, "unknown army to reinforce"
    assert not is_defeated_army(s, a), "defeated army cannot be reinforced"
    assert reinforcement_units(s, a) > 0, "reinforcement units have to be strictly positive"

    u_a = reinforcement_units(s, a)
    T_a = list(territories_occupied_by_army(s, a))
    shuffle(T_a)
    N_a = [ n_a
            for i in range(len(T_a))
            if (n_a := u_a // len(T_a) + (1 if i < u_a % len(T_a) else 0)) > 0 ]
    result = dict(zip(T_a, N_a))

    assert all(territory_occupant(s, t) == a for t in result), "The selected territories belong to the army"
    assert all(result[t] > 0 for t in result), "Each selected territory must receive at least one unit"
    assert sum(result[t] for t in result) == reinforcement_units(s, a), "The sum of all the reinforcement units must be equal to {reinforcement_units(s, a)}"
    assert all(abs(result[t_0] - result[t_1]) <= 1 for t_0 in result for t_1 in result), "uniform distribution of the units"

    return result


def border_reinforcement(s: State,
                         a: Army) -> Dict[Territory, Unit]:
    """
    Simple border reinforcement strategy (safe version).
    Distributes reinforcements only among border territories (those touching enemies).
    If there are more borders than units, reinforces the most exposed ones first.
    """
    assert isinstance(s, State)
    assert isinstance(a, Army)
    assert a in s.world.armies, "unknown army to reinforce"
    assert not is_defeated_army(s, a), "defeated army cannot be reinforced"
    assert reinforcement_units(s, a) > 0, "reinforcement units must be > 0"

    from model.state_informations import bordering_territories, territory_units

    u_a = reinforcement_units(s, a)
    T_a = list(territories_occupied_by_army(s, a))


    borders = [t for t in T_a
               if any(territory_occupant(s, t_b) != a
                      for t_b in bordering_territories(s, t))]


    if not borders:
        return random_uniform_reinforcement(s, a)


    if len(borders) > u_a:

        borders = sorted(
            borders,
            key=lambda t: sum(
                territory_units(s, t_b)
                for t_b in bordering_territories(s, t)
                if territory_occupant(s, t_b) != a
            ),
            reverse=True
        )[:u_a]

    k = len(borders)
    base = max(1, u_a // k)
    result = {t: base for t in borders}
    remaining = u_a - base * k

    from random import sample
    for t in sample(borders, remaining):
        result[t] += 1

    # Postconditions
    assert all(territory_occupant(s, t) == a for t in result)
    assert all(result[t] > 0 for t in result), "strictly positive reinforcement units per territory"
    assert sum(result.values()) == reinforcement_units(s, a)

    return result

from probabilities_single_battle import (
    all_battles_11, all_battles_12,
    all_battles_21, all_battles_22,
    all_battles_31, all_battles_32
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


def advanced_proha_reinforcement(s: State,
                         a: Army,
                         iterations: int = 100) -> Dict[Territory, Unit]:
    """
    MCTS-based reinforcement tuner.
    Simulates attack viability after hypothetical reinforcements to allocate troops optimally.
    """

    # TUNING BLOCK 
    PROBE = 2           
    THRESHOLD = 1    
    DISCARD_BELOW = 0.1  

    from random import random
    import math
    from model.state_informations import (
        bordering_territories, territories_occupied_by_army,
        territory_units, territory_occupant,
        reinforcement_units as RU, is_defeated_army
    )

    def sample_from_outcomes(outcomes):
        r = random()
        acc = 0.0
        for pa, pd, p in outcomes:
            acc += p
            if r <= acc:
                return pa, pd
        return outcomes[-1][0], outcomes[-1][1]

    def simulate_one_battle(a_u, d_u):
        while a_u > 1 and d_u > 0:
            att_dice = min(3, a_u - 1)
            def_dice = min(2, d_u)
            pa, pd = sample_from_outcomes(battle_outcomes[(att_dice, def_dice)])
            a_u -= pa
            d_u -= pd
        return 1 if d_u <= 0 else 0

    def avg_win_prob(a_u, d_u, iters):
        wins = 0
        for _ in range(iters):
            wins += simulate_one_battle(a_u, d_u)
        return wins / iters


    # Preconditions
    assert isinstance(s, State)
    assert isinstance(a, Army)
    assert a in s.world.armies and not is_defeated_army(s, a)

    u_total = RU(s, a)
    T_a = list(territories_occupied_by_army(s, a))
    if not T_a:
        return {}

    scores = {}


    # Scoring phase
    for t in T_a:
        base = territory_units(s, t)
        best = 0.0
        for nb in bordering_territories(s, t):
            if territory_occupant(s, nb) != a:
                prob = avg_win_prob(base + PROBE, territory_units(s, nb), iterations)
                best = max(best, prob)

        # discard hopeless fronts
        if best < DISCARD_BELOW:
            weight = 0.0
        # high priority (1.0) if near threshold from below
        elif best < THRESHOLD:
            weight = 1.0
        # no reward (0.0) for already-strong fronts
        else:
            weight = 0.0

        scores[t] = max(weight, 1e-6)


    # Allocation phase (proportional)
    total = sum(scores.values())
    if total == 0:
        per = u_total // len(T_a)
        res = {t: per for t in T_a}
        res[T_a[0]] += u_total - sum(res.values())
        return res

    raw = {t: u_total * (scores[t] / total) for t in T_a}
    result = {t: int(v) for t, v in raw.items() if int(v) > 0}
    rem = u_total - sum(result.values())

    if rem > 0:
        order = sorted(T_a, key=lambda t: raw[t] - int(raw[t]), reverse=True)
        i = 0
        while rem > 0:
            t = order[i % len(order)]
            result[t] = result.get(t, 0) + 1
            rem -= 1
            i += 1

    if not result:
        result[max(T_a, key=lambda t: scores[t])] = u_total

    assert sum(result.values()) == u_total
    return result