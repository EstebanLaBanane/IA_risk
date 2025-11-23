from strategy.strategy import Strategy
from strategy.reinforcements import( random_reinforcement, random_uniform_reinforcement)
from strategy.defenses import random_defense, maximum_defense
from strategy.invasions import random_uniform_invasion, uniform_invasion
from strategy.maneuvers import random_maneuver, random_uniform_maneuver,random_uniform_largest_maneuver

from strategy.attacksHamza import safe_attack,UCB_attack
from strategy.defensesHamza import minimal_defense
from strategy.invasionsHamza import aggressive_invasion
from strategy.maneuversHamza import border_maneuver
from strategy.reinforcementsHamza import border_reinforcement, advanced_proha_reinforcement

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

