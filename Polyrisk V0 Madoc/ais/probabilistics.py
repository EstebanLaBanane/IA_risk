from strategy.strategy import Strategy
from strategy.reinforcements import( random_reinforcement, random_uniform_reinforcement, advanced_proha_reinforcement,
border_reinforcement,)
from strategy.attacks import random_attack, safe_attack,UCB_attack
from strategy.defenses import random_defense, maximum_defense,minimal_defense
from strategy.invasions import random_uniform_invasion, uniform_invasion,aggressive_invasion
from strategy.maneuvers import random_maneuver, random_uniform_maneuver,border_maneuver,random_uniform_largest_maneuver


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

