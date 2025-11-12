from strategy.strategy import Strategy


"""
This class inherits from Strategy and implements a list of defenses to the format [{territory_defending : units, territory_attacking : units},{...}].
This is used to launch counter-attacks
"""
class StrategyPorcupine(Strategy):
    last_round_defenses : list[dict] = []