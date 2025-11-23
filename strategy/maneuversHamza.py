from typing import Tuple, Optional
from random import randint, choice
from model.region import Unit
from model.territory import Territory
from model.army import Army
from model.state import State
from model.state_informations import territory_occupant, territory_units, bordering_territories, territories_occupied_by_army, army_adjacent_territories


def random_maneuver (s: State,
                     a: Army) -> Optional[Tuple[Territory, Territory, Unit]]:
    """
    A totally random maneuver.

    :post:  Effective unless the army has only isolated territories or no more than one unit left
    """
    assert isinstance(s, State)
    assert isinstance(a, Army)
    assert a in s.world.armies, "The army must belong to the current state"

    M = [ (t_0, t_1, randint(1, u_t_0 - 1))
          for (t_0, t_1) in army_adjacent_territories(s, a)
          if (u_t_0 := territory_units(s, t_0)) > 1 ]
    result = ( None      if len(M) == 0 else
               choice(M) )

    if result is not None:
        (t_0, t_1, n) = result
        assert isinstance(t_0, Territory)
        assert isinstance(t_1, Territory)
        assert t_0 in s.state, "The starting territory belongs to the current state"
        assert t_1 in s.state, "The ending territory belongs to the current state"
        assert territory_occupant(s, t_0) == a, "The starting territory is occupied by the army"
        assert territory_occupant(s, t_1) == a, "The defending territory is occupied by the army"
        assert n > 0, "At least one unit is maneuvering"
        assert n < territory_units(s, t_0), "At least one unit must be left behind"
    else:
        assert all(territory_occupant(s, b) != a
                   for t in territories_occupied_by_army(s, a)
                   if territory_units(s, t) > 1
                   for b in bordering_territories(s, t)), "Effective unless the army has only isolated territories or no more than one unit left"

    return result

def border_maneuver(s: State,
                    a: Army) -> Optional[Tuple[Territory, Territory, Unit]]:
    """
    Simple smart maneuver: move units from safe inner territories (no enemy neighbors)
    toward adjacent border territories (enemy nearby).
    Only moves between adjacent friendly territories.
    Fallback: if no valid move, returns random_maneuver(s, a).
    """
    assert isinstance(s, State)
    assert isinstance(a, Army)
    assert a in s.world.armies, "The army must belong to the current state" 

    inner = []
    borders = []
    for t in territories_occupied_by_army(s, a):
        neighbors = list(bordering_territories(s, t))
        if any(territory_occupant(s, n) != a for n in neighbors):
            borders.append(t)
        elif territory_units(s, t) > 1:
            inner.append(t)

    moves = []
    for t_0 in inner:
        for t_1 in borders:
            if (t_0, t_1) in s.world.adjacencies:
                u_src = territory_units(s, t_0)
                if u_src > 1:
                    n_move = max(1, u_src // 2)
                    moves.append((t_0, t_1, n_move))

    if not moves:
        # fallback to random maneuver if nothing to do
        return random_maneuver(s, a)

    t_0, t_1, n = max(moves, key=lambda m: m[2])
    assert (t_0, t_1) in s.world.adjacencies
    assert territory_occupant(s, t_0) == a
    assert territory_occupant(s, t_1) == a
    assert 0 < n < territory_units(s, t_0)

    return (t_0, t_1, n)

