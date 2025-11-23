__all__ = [
    'bordering_troups',
    'border_territories',
    'is_border_territory',
    'reachable_territories',
]

from typing import Optional, Set, Tuple
from model.region import Region, Unit
from model.territory import Territory
from model.army import Army
from model.state import State
from model.state_informations import bordering_territories, territory_occupant, territory_units, territories_occupied_by_army


def bordering_troups(s : State, t : Territory, occupant : Army, excluded_territory : None | Territory = None) -> int:
    """
    Returns the number of enemy troups adjacent to the given territory, if 0 all of the neighboring territories are allies.
    If an excluded_territory is specified : it will not be taken into account as an enemy territory (used when an army has not yet invaded a territory but considers it its own)
    """
    neighbors= bordering_territories(s,t)
    enemy_troup_counter = 0
    for neighbor in neighbors:
        if territory_occupant(s,neighbor) != occupant and neighbor != excluded_territory:
            enemy_troup_counter += territory_units(s,neighbor)
    return enemy_troup_counter

def border_territories(s : State, a : Army) -> list:
    """
    Returns the territories with enemy neighbors and the number of enemy units around. Format : [[Territory, enemy units],[...]] sorted descending by enemy units.
    
    Input :
            s : State = Game state
            a : Army = army for which we find border territories
    """
    border_territories = []
    T_a = list(territories_occupied_by_army(s, a))
    for i in range(0, len(T_a)):
        territory : Territory = T_a[i]
        neighboring_units = bordering_troups(s,territory,a)
        if neighboring_units > 0:
            border_territories.append([territory,neighboring_units])
    border_territories = sorted(border_territories, key=lambda x:x[1],reverse=True)
    return border_territories

def is_border_territory(s :State, a : Army, t : Territory, excluded_territory : None | Territory = None) -> bool:
    """
    Returns true if the territory t is a border territory (ie. has neighboring enemy territory of the army a) regardless if the territory t is in the army a
    If an excluded_territory is specified : it will not be taken into account as an enemy territory (used when an army has not yet invaded a territory but considers it its own)
    """
    for territory in bordering_territories(s,t):
        if territory_occupant(s,territory) != a:
            if excluded_territory is None:
                return True
            elif territory != excluded_territory:
                return True
    return False

def reachable_territories(s :State, a : Army, t : Territory,excluded_territories : None | Set[Territory] = None) -> list:
    result = []
    for territory in bordering_territories(s,t):
        if territory_occupant(s,territory) != a:
            continue
        if excluded_territories is None:
            result.append(territory)
            new_excluded = [t]
            result += reachable_territories(s,a,territory,new_excluded)
        elif territory not in excluded_territories:
            result.append(territory)
            new_excluded = excluded_territories+ [t]
            result += reachable_territories(s,a,territory,new_excluded)

    return list(set(result))