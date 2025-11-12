#! /bin/python
# gvim: set fileencoding=utf-8
#
# (c) September 11, 2025, José Martinez, Polytech Nantes, University of Nantes
#
# Licence:  proprietary
# The use of this library is not authorised outside the Polytechnic School of the University of Nantes.
#


"""
Several strategies are provided in order to invade a conquered territory.

Notice that the pre- and post-conditions of these functions would not need to be tested.
They are already ensured by the strategies.
However, they are repeated to the programmer for clarity and documentation.
Also, this allows to detect a possible flaw closer to its source.
A model is given below.
Notice that post-conditions can be strengthen.

def model_of_invasion_function (s:   State,
                                t_a: Territory,
                                t_d: Territory,
                                n_a: Unit,
                                p_a: Unit) -> Unit:
    '''
    :parameter s:  the current state
    :parameter t_a:  the attacking territory
    :parameter t_d:  the defended but to be lost territory
    :parameter n_a:  the number of engaged units by the attacker
    :parameter p_a:  the number of lost units of the attacker

    :pre:  The attacking territory must belong to the current state
    :pre:  The defending territory must belong to the current state
    :pre:  The armies of the two territories must be distinct
    :pre:  At least one unit must invade

    :return n:  the number of invading units

    :post:  At least the left units from the last battle must invade, i.e., n_a - p_a
    :post:  At least one unit must be left behind
    '''
    # PRE-CONDITION
    assert isinstance(s, State)
    assert isinstance(t_a, Territory)
    assert isinstance(t_d, Territory)
    assert t_a in s.state, "The attacking territory must belong to the current state"
    assert t_d in s.state, "The defending territory must belong to the current state"
    assert territory_occupant(s, t_a) != territory_occupant(s, t_d), "The armies of the two territories must be distinct"
    assert n_a > 0, "At least one unit must invade"

    result = DO_SOME_STUFF

    # POST-CONDITION
    assert n_a - p_a <= result, f"At least the left units from the last battle must invade, i.e., {n_a} - {p_a} = {n_a - p_a}"
    assert result <= territory_units(s, t_a) - p_a - 1, "At least one unit must be left behind"

    return result
"""


__all__ = [
    'minimal_invasion',
    'random_uniform_invasion',
    'uniform_invasion',
    ]

from random import randint
from model.region import Unit
from model.territory import Territory
from model.state import State
from model.state_informations import territory_occupant, territory_units, is_border_territory, bordering_troups


def minimal_invasion (s:   State,
                      t_a: Territory,
                      t_d: Territory,
                      n_a: Unit,
                      p_a: Unit) -> Unit:
    """
    Only the attacking and victorious units enter the new territory.
    """
    assert isinstance(s, State)
    assert isinstance(t_a, Territory)
    assert isinstance(t_d, Territory)
    assert t_a in s.state, "The attacking territory must belong to the current state"
    assert t_d in s.state, "The defending territory must belong to the current state"
    assert territory_occupant(s, t_a) != territory_occupant(s, t_d), "The armies of the two territories must be distinct"
    assert n_a > 0, "At least one unit must invade"

    result = n_a - p_a

    assert n_a - p_a <= result, f"At least the left units from the last battle must invade, i.e., {n_a} - {p_a} = {n_a - p_a}"
    assert result <= territory_units(s, t_a) - p_a - 1, "At least one unit must be left behind"

    return result


def random_uniform_invasion (s:   State,
                             t_a: Territory,
                             t_d: Territory,
                             n_a: Unit,
                             p_a: Unit) -> Unit:
    """
    The attacking and victorious units plus a random number of additional units enter the new territory.
    """
    assert isinstance(s, State)
    assert isinstance(t_a, Territory)
    assert isinstance(t_d, Territory)
    assert t_a in s.state, "The attacking territory must belong to the current state"
    assert t_d in s.state, "The defending territory must belong to the current state"
    assert territory_occupant(s, t_a) != territory_occupant(s, t_d), "The armies of the two territories must be distinct"
    assert n_a > 0, "At least one unit must invade"

    result = max(n_a - p_a, randint(1, territory_units(s, t_a) - 1))

    assert n_a - p_a <= result, f"At least the left units from the last battle must invade, i.e., {n_a} - {p_a} = {n_a - p_a}"
    assert result <= territory_units(s, t_a) - p_a - 1, "At least one unit must be left behind"

    return result


def uniform_invasion (s:   State,
                      t_a: Territory,
                      t_d: Territory,
                      n_a: Unit,
                      p_a: Unit) -> Unit:
    """
    The remaining units of the attacker are split evenly between the attacking territory and the conquered one.
    """
    assert isinstance(s, State)
    assert isinstance(t_a, Territory)
    assert isinstance(t_d, Territory)
    assert t_a in s.state, "The attacking territory must belong to the current state"
    assert t_d in s.state, "The defending territory must belong to the current state"
    assert territory_occupant(s, t_a) != territory_occupant(s, t_d), "The armies of the two territories must be distinct"
    assert n_a > 0, "At least one unit must invade"

    result = max(n_a - p_a, (territory_units(s, t_a) - p_a) // 2)

    assert n_a - p_a <= result, f"At least the left units from the last battle must invade, i.e., {n_a} - {p_a} = {n_a - p_a}"
    assert result <= territory_units(s, t_a) - p_a - 1, "At least one unit must be left behind"

    return result


def border_invasion (s:   State,
                    t_a: Territory,
                    t_d: Territory,
                    n_a: Unit,
                    p_a: Unit) -> Unit:

    """
    The remaining units will be either : 
                                        -transferred completely if the attacking territory becomes an 'inside' territory (ie surrounded only by allies)
                                        -shared between the two territories based on the number of adjacent enemy troups
                                        -Stay in the attacking territory and give only one to the invaded territory if it is an 'inside' territory
    """

    # PRE-CONDITION
    assert isinstance(s, State)
    assert isinstance(t_a, Territory)
    assert isinstance(t_d, Territory)
    assert t_a in s.state, "The attacking territory must belong to the current state"
    assert t_d in s.state, "The defending territory must belong to the current state"
    assert territory_occupant(s, t_a) != territory_occupant(s, t_d), "The armies of the two territories must be distinct"
    assert n_a > 0, "At least one unit must invade"

    result = None

    attacker_army = territory_occupant(s,t_a)
    if not is_border_territory(s,attacker_army,t_a,t_d):
        result = territory_units(s, t_a) - p_a - 1
    elif not is_border_territory(s,attacker_army,t_d):
        result = n_a - p_a
    else:
        available_troups = territory_units(s, t_a) - p_a - 1
        threat_attacker_territory = bordering_troups(s,t_a,attacker_army,t_d)
        threat_defender_territory = bordering_troups(s,t_d,attacker_army)
        total_bordering_troups = threat_attacker_territory + threat_defender_territory

        troups_defender = max(round( available_troups*(threat_defender_territory/total_bordering_troups)), n_a-p_a)

        result = troups_defender



    # POST-CONDITION
    assert n_a - p_a <= result, f"At least the left units from the last battle must invade, i.e., {n_a} - {p_a} = {n_a - p_a}"
    assert result <= territory_units(s, t_a) - p_a - 1, "At least one unit must be left behind"

    return result