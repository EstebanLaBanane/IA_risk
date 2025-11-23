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
    assert reinforcement_units(s, a) > 0, "reinforcements units have to be strictly positive"

    result = DO_SOME_STUFF

    # POST-CONDITION
    assert all(result[t].army == a for t in result), "The selected territories belong to the army"
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
from model.state_informations import is_defeated_army, territories_occupied_by_army, reinforcement_units, territory_occupant, border_territories,territory_units 


def random_reinforcement (s: State,
                          a: Army) -> Dict[Territory, Unit]:
    """
    A random sub-set of the territories receives a random number of units.
    """
    assert isinstance(s, State)
    assert isinstance(a, Army)
    assert a in s.world.armies, "unknown army to reinforce"
    assert not is_defeated_army(s, a), "defeated army cannot be reinforced"
    assert reinforcement_units(s, a) > 0, "reinforcements units have to be strictly positive"

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
    assert reinforcement_units(s, a) > 0, "reinforcements units have to be strictly positive"

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

