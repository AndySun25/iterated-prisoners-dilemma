import uuid

from moves import outcomes, ess_result_map


class Entity:
    max_age = 50
    maturity_age = 45

    def __init__(self, strategy_class) -> None:
        self.strategy_class = strategy_class
        self.memory = {}
        self.uuid = uuid.uuid4()
        self.age = 0
        self.hit_points = 1
        self.has_reproduced = False

    def get_strategy_instance(self, opponent: 'Entity'):
        try:
            return self.memory[opponent.uuid]
        except KeyError:
            strategy_instance = self.strategy_class()
            self.memory[opponent.uuid] = strategy_instance
            return strategy_instance

    def reproduce(self):
        self.has_reproduced = True
        return Entity(strategy_class=self.strategy_class)

    def apply_results(self, result):
        self.age += 1
        self.hit_points += ess_result_map[result]


class MatchMaker:
    def _play_round(self, strategy_1, strategy_2):
        strategy_1_move = strategy_1.get_next_move()
        strategy_2_move = strategy_2.get_next_move()

        strategy_1_result = outcomes[strategy_1_move][strategy_2_move]
        strategy_2_result = outcomes[strategy_2_move][strategy_1_move]

        strategy_1.post_move(strategy_1_move, strategy_2_move)
        strategy_2.post_move(strategy_2_move, strategy_1_move)

        # print("%s (%s) - (%s) %s" % (strategy_1.name, strategy_1_move.value, strategy_2_move.value, strategy_2.name))

        return strategy_1_result, strategy_2_result

    def play_strategies(self, strategy_class_1, strategy_class_2, rounds):
        results = []
        strategy_1 = strategy_class_1()
        strategy_2 = strategy_class_2()
        for i in range(rounds):
            results.append(self._play_round(strategy_1, strategy_2))
        return results

    def play_entities(self, entity_1: Entity, entity_2: Entity):
        entity_1_strategy = entity_1.get_strategy_instance(entity_2)
        entity_2_strategy = entity_2.get_strategy_instance(entity_1)
        r1, r2 = self._play_round(entity_1_strategy, entity_2_strategy)
        entity_1.apply_results(r1)
        entity_2.apply_results(r2)
