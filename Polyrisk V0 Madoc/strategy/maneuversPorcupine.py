from typing import Tuple, Optional
from random import randint, choice
from model.region import Unit
from model.territory import Territory
from model.army import Army
from model.state import State
from model.state_informations import territory_occupant, territory_units, bordering_territories, territories_occupied_by_army
from model.custom_state_informations import is_border_territory, bordering_troups

def edge_maneuvers (s: State,
                a: Army) -> Optional[Tuple[Territory, Territory, Unit]]:

    """
    Troups are moved to 'repair damages', ie reinforce territories that lost troups defending attacks
    """

    # PRE-CONDITION
    assert isinstance(s, State)
    assert isinstance(a, Army)
    assert a in s.world.armies, "The army must belong to the current state" 
    
    result = None

    # for territory in territories_occupied_by_army(s,a):
    #     if is_border_territory(s,a,territory) or territory_units(s,territory) == 1:
    #         continue
    #     reachable = reachable_territories(s,a,territory)
    #     # FORMAT [[territory,nb_enemy_units],[...]]
    #     reachable_border_territories = []
    #     for reachable_territory in reachable:
    #         if not is_border_territory(s,a,reachable_territory):
    #             continue
    #         reachable_border_territories.append([reachable_territory,bordering_troups(s,reachable_territory,a)])


    #     reachable_border_territories = sorted(reachable_border_territories, key=lambda x:x[1],reverse=True)
    #     target = reachable_border_territories[0][0]

    #     distance(target,reachable)

    #     return [territory,...,territory_units(s,territory)-1]
    
    border_territories = []
    for territory in territories_occupied_by_army(s,a):

        if is_border_territory(s,a,territory) or territory_units(s,territory) == 1:
            continue
        for neighbor in bordering_territories(s,territory):
            if not is_border_territory(s,a,neighbor):
                continue
            border_territories.append([territory,neighbor,territory_units(s,territory)-1,bordering_troups(s,neighbor,a)])
    
    border_territories = sorted(
        border_territories,
        key=lambda x: (-x[2], -x[3])  # on inverse le signe pour un tri décroissant du premier critère
    )
    
    if len(border_territories):
        return [border_territories[0][0],border_territories[0][1],border_territories[0][2]]




    # POST-CONDITION
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

    return result