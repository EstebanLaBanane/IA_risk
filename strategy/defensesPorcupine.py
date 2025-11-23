from model.region import Unit
from model.territory import Territory
from model.state import State
from model.state_informations import territory_occupant, territory_units
from strategy.strategyPorcupine import StrategyPorcupine

def maximum_porcupine_defense (s:   State,
                     t_a: Territory,
                     t_d: Territory,
                     n:   Unit) -> Unit:
    """
    Always the largest number of units, i.e., 2 when possible, otherwise the single remaining unit.
    """
    assert isinstance(s, State)
    assert isinstance(t_a, Territory)
    assert isinstance(t_d, Territory)
    assert t_a in s.state, "The attacking territory belongs to the state of the game"
    assert t_d in s.state, "The defending territory belongs to the state of the game"
    assert territory_occupant(s, t_a) != territory_occupant(s, t_d), "The attacker and the defender are different armies"
    assert n > 0, "At least one unit is attacking"
    assert n < territory_units(s, t_a), "No more than the available units minus one can attack"
    assert n <= 3, "No more than three units can attack, independently of the accumulated troops"
    assert territory_units(s, t_d) >= 1, "The territory under attack can defend itself"
    strategy : StrategyPorcupine = territory_occupant(s,t_d).strategy
    result = ( 1 if territory_units(s, t_d) == 1 else
               2 )
    report = [t_d,t_a]
    strategy.last_round_defenses.append(report)
    assert result in { 1, 2 }, "Only one or two units can defend"
    assert result <= territory_units(s, t_d), f"The number of defending units is limited by the number of available units: {s.state[t_d][1]}"

    return result