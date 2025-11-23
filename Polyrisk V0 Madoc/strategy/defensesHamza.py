#! /bin/python
# gvim: set fileencoding=utf-8
#
# (c) September 8, 2025, José Martinez, Polytech Nantes, University of Nantes
#
# Licence:  proprietary
# The use of this library is not authorised outside the Polytechnic School of the University of Nantes.
#


"""
Several strategies are provided in order to oppose an attacker.

Notice that the pre- and post-conditions of these functions would not need to be tested.
They are already ensured by the strategies.
However, they are repeated to the programmer for clarity and documentation.
Also, this allows to detect a possible flaw closer to its source.
A model is given below.
Notice that post-conditions can be strengthen.

def model_of_defense_function (s:   State,
                               t_a: Territory,
                               t_d: Territory,
                               n:   Unit) -> Unit:
    '''
    :parameter s:  a current state
    :parameter a:  an army to reinforce

    :pre:  The attacking territory belongs to the state of the game
    :pre:  The defending territory belongs to the state of the game
    :pre:  The attacker and the defender are different armies
    :pre:  At least one unit is attacking
    :pre:  No more than the available units minus one can attack
    :pre:  No more than three units can attack, independently of the accumulated troops
    :pre:  The territory under attack can defend itself

    :post:  Only one or two units can defend
    :post:  The number of defending units is limited by the number of available units
    '''
    # PRE-CONDITION
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

    result = DO_SOME_STUFF

    # POST-CONDITION
    assert result in { 1, 2 }, "Only one or two units can defend"
    assert result <= territory_units(s, t_d), f"The number of defending units is limited by the number of available units: {s.state[t_d][1]}"

    return result
"""


__all__ = [
    'random_defense',
    'maximum_defense',
    ]


from random import randint
from model.region import Unit
from model.territory import Territory
from model.state import State
from model.state_informations import territory_occupant, territory_units

def minimal_defense (s:   State,
                     t_a: Territory,
                     t_d: Territory,
                     n:   Unit) -> Unit:
    """
    Always defend with only one unit, even if more units are available.
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

    result = 1

    assert result in { 1, 2 }, "Only one or two units can defend"
    assert result <= territory_units(s, t_d), f"The number of defending units is limited by the number of available units: {s.state[t_d][1]}"

    return result
