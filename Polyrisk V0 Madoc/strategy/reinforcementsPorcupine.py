from typing import Dict
from random import shuffle, randint, sample, choice
from model.region import Unit
from model.territory import Territory
from model.state import State
from model.army import Army
from model.state_informations import is_defeated_army, reinforcement_units, territory_occupant, border_territories,territory_units 

def border_reinforcement (s: State,
                          a: Army) -> Dict[Territory, Unit]:

    """
    The new units are distributed among the borders of the army (ie. territories adjacent to enemy territoires), 
    bonuses are distributed to the territories with the most enemy troups adjacent.
    """

    # PRE-CONDITION
    assert isinstance(s, State)
    assert isinstance(a, Army)
    assert a in s.world.armies, "unknown army to reinforce"
    assert not is_defeated_army(s, a), "defeated army cannot be reinforced"
    assert reinforcement_units(s, a) > 0, "reinforcements units have to be strictly positive"

    result = {}
    
    # At the end of the processing border_territories will follow this format :
    # [ [Territory, neighboring_units, unanswered_units], [...] ]
    # where unanswered_units equals the neighboring_units + 3 minus the units in the territory or 0 if the result was negative
    b_territories = border_territories(s,a)

    for border_territory in b_territories:
        border_territory.append(max(border_territory[1]+3-territory_units(s,border_territory[0]),0))

    total_unanswered_neighboring_troups = 0
    for border_territory in b_territories:
        total_unanswered_neighboring_troups += border_territory[2]

    b_territories = sorted(
        b_territories,
        key=lambda x: (-x[2], -x[1])  # on inverse le signe pour un tri décroissant du premier critère
    )

    del border_territory

    start_units = reinforcement_units(s, a)
    remaining_units = start_units
    if b_territories[0][2] == 0:
        for border_territory in b_territories:
            if remaining_units <= 0:
                break
            awarded_units = max(round(start_units/len(b_territories)), 1)
            result[border_territory[0]] = awarded_units
            remaining_units -= awarded_units
  

        del remaining_units

        diff = sum(result[t] for t in result) - reinforcement_units(s,a)
        start_sum = sum(result[t] for t in result)
        if diff> 0:
            # To avoid a case where decrementing reinforcement means 0
            if result[list(result)[-1]] == diff:
                result.pop(list(result)[-1])
            elif result[list(result)[-1]] > diff:
                result[list(result)[-1]] -= abs(diff)
            else:
                new_diff = diff - result[list(result)[-1]]
                result.pop(list(result)[-1])
                result[list(result)[-1]] -= abs(new_diff)

        elif diff<0:
            result[list(result)[-1]] += abs(diff)
        
        # POST-CONDITION
        assert all(territory_occupant(s, t) == a for t in result), "The selected territories belong to the army"
        # if not all(result[t] > 0 for t in result):
        #     print("supposed : ",reinforcement_units(s,a))
        #     print("reality : ",sum(result[t] for t in result))
        #     print("result : ",result)
        #     print("diff : ",diff)
        #     print("start sum : ",start_sum)
        #     print("recalculed : ",sum(result[t] for t in result) - reinforcement_units(s,a))
        assert all(result[t] > 0 for t in result), "Each selected territory must receive at least one unit"
        
        # if sum(result[t] for t in result) != reinforcement_units(s,a):
        #     print("supposed : ",reinforcement_units(s,a))
        #     print("reality : ",sum(result[t] for t in result))
        #     print("result : ",result)
        #     print("diff : ",diff)
        #     print("start sum : ",start_sum)
        #     print("recalculed : ",sum(result[t] for t in result) - reinforcement_units(s,a))
        assert sum(result[t] for t in result) == reinforcement_units(s, a), "The sum of all the reinforcement units must be equal to {reinforcement_units(s, a)}"            
        return result


    for border_territory in b_territories:
        if remaining_units <= 0:
            break
        #max(total_unanswer,0) to avoid division by zero
        value = start_units * (border_territory[2]/max(total_unanswered_neighboring_troups,1))
        awarded_units = min(max(round(value),1),remaining_units)
        remaining_units -= awarded_units
        result[border_territory[0]] = awarded_units
    
    diff = sum(result[t] for t in result) - reinforcement_units(s,a)
    start_sum = sum(result[t] for t in result)
    if diff> 0:
        # To avoid a case where decrementing reinforcement means 0
        if result[list(result)[-1]] == diff:
            result.pop(list(result)[-1])
        elif result[list(result)[-1]] > diff:
            result[list(result)[-1]] -= abs(diff)
        else:
            new_diff = diff - result[list(result)[-1]]
            result.pop(list(result)[-1])
            result[list(result)[-1]] -= abs(new_diff)

    elif diff<0:
        result[list(result)[-1]] += abs(diff)

    # POST-CONDITION
    assert all(territory_occupant(s, t) == a for t in result), "The selected territories belong to the army"
    assert all(result[t] > 0 for t in result), "Each selected territory must receive at least one unit"
    assert sum(result[t] for t in result) == reinforcement_units(s, a), "The sum of all the reinforcement units must be equal to {reinforcement_units(s, a)}"

    return result