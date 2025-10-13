"""
Porcupine players are AIs.
They are not dangerous by themselves as they do not attack unless they have defended an attack.
However, they will build a very strong defense and force the player get rid of them early or concentrate all of their ressources on an attack.
"""

__all__ = [
    'strategy_porcupine',
    ]


from strategy.strategy import Strategy
from strategy.reinforcements import border_reinforcement
from strategy.attacks import counter_attack
from strategy.defenses import maximum_defense
from strategy.invasions import border_invasion
from strategy.maneuvers import repairements


strategy_porcupine = Strategy("Porcupine",
                                 border_reinforcement,
                                 counter_attack,
                                 maximum_defense,
                                 border_invasion,
                                 repairements)
