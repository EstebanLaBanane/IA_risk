from typing import Tuple, Optional
from model.region import Unit
from model.army import Army
from model.territory import Territory
from model.state import State
from model.state_informations import territory_occupant, territory_units, is_defeated_army
from strategy.strategyPorcupine import StrategyPorcupine

def counter_attack (s: State,
                    a: Army) -> Optional[Tuple[Territory, Territory, Unit]]:
    
    """
    An attack is only launched on a territory after defending an attack from it.
    Last round's attacks are stored in the StrategyPorcupine class
    """

    # PRE-CONDITION
    assert isinstance(s, State)
    assert isinstance(a, Army)
    assert a in s.world.armies, "The army must belong to the current state"
    assert not is_defeated_army(s, a), "The army must not be defeated"
    porcupine : StrategyPorcupine = a.strategy
    result = None
    for defense in porcupine.last_round_defenses:
        t_d = defense[0]
        t_a = defense[1]
        porcupine.last_round_defenses = porcupine.last_round_defenses[1:]
        if territory_occupant(s,t_d) == a and territory_occupant(s,t_a) != a and territory_units(s,t_d)>1 and territory_units(s,t_d)>= territory_units(s,t_a)+3:
            # MAXIMUM COUNTER ATTACK
            result = [t_d,t_a,min(territory_units(s,t_d)-1,3)]
            break

    # POST-CONDITION
    if result is not None:
        (t_a, t_d, n) = result
        assert isinstance(t_a, Territory)
        assert isinstance(t_d, Territory)
        assert t_a in s.state, "The attacking territory belongs to the current state"
        assert t_d in s.state, "The defending territory belongs to the current state"
        assert territory_occupant(s, t_a) == a, "The attacking territory is occupied by the army"
        assert territory_occupant(s, t_d) != a, "The defending territory is not occupied by the army"
        assert n in { 1, 2, 3 }, "The attacking units is between one and three"
        assert n < territory_units(s, t_a), "The attacking units is strictly less than the number of available units"
    return result