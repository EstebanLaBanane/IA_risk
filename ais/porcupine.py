"""
Porcupine players are AIs.
They are not dangerous by themselves as they do not attack unless they have defended an attack.
However, they will build a very strong defense and force the player get rid of them early or concentrate all of their ressources on an attack.
"""

__all__ = [
    'strategy_porcupine',
    ]


from strategy.strategyPorcupine import StrategyPorcupine
from strategy.reinforcementsPorcupine import border_reinforcement
from strategy.attacksPorcupine import counter_attack
from strategy.defensesPorcupine import maximum_porcupine_defense
from strategy.invasionsPorcupine import border_invasion
from strategy.maneuversPorcupine import edge_maneuvers


strategy_porcupine = StrategyPorcupine("Porcupine",
                                 border_reinforcement,
                                 counter_attack,
                                 maximum_porcupine_defense,
                                 border_invasion,
                                 edge_maneuvers)
