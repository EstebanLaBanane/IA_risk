from model.region import Unit
from model.territory import Territory
from model.state import State
from model.state_informations import territory_occupant, territory_units

def aggressive_invasion(s:   State,
                        t_a: Territory,
                        t_d: Territory,
                        n_a: Unit,
                        p_a: Unit) -> Unit:
    """
    Aggressive invasion strategy:
    move as many units as possible into the conquered territory,
    keeping only one unit behind in the origin.

    Stronger than uniform/random invasion.
    """
    assert isinstance(s, State)
    assert isinstance(t_a, Territory)
    assert isinstance(t_d, Territory)
    assert t_a in s.state and t_d in s.state
    assert territory_occupant(s, t_a) != territory_occupant(s, t_d)
    assert n_a > 0, "At least one unit must invade"

    u_a = territory_units(s, t_a)
    left = max(1, (u_a - p_a) - 1) 
    result = max(n_a - p_a, left)

    assert n_a - p_a <= result, f"At least {n_a - p_a} must invade"
    assert result <= territory_units(s, t_a) - p_a - 1, "At least one unit must be left behind"

    return result