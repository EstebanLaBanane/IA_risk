from strategy.strategy import Strategy
from strategy.reinforcementsHamza import(advanced_proha_reinforcement,border_reinforcement,)
from strategy.attacksHamza import safe_attack,UCB_attack
from strategy.defenses import  maximum_defense
from strategy.invasionsHamza import aggressive_invasion
from strategy.maneuversHamza import border_maneuver
from strategy.invasions import random_uniform_invasion
from strategy.maneuvers import random_uniform_maneuver


strategy_safe = Strategy("safe_strategy",
    border_reinforcement,
    safe_attack,
    maximum_defense,
    aggressive_invasion,
    border_maneuver
)

strategy_UCB = Strategy(
    "UCB_attack",
    advanced_proha_reinforcement,
    UCB_attack,
    maximum_defense,
    random_uniform_invasion,
    random_uniform_maneuver
)

