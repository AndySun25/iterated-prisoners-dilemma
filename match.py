import uuid

from moves import outcomes


class Entity:
    def __init__(self, strategy_class) -> None:
        self.strategy_class = strategy_class
        self.memory = {}
        self.uuid = uuid.uuid4()

    def get_strategy_instance(self, opponent: 'Entity'):
        try:
            return self.memory[opponent.uuid]
        except KeyError:
            strategy_instance = self.strategy_class()
            self.memory[opponent.uuid] = strategy_instance
            return strategy_instance


class Match:
    def __init__(self, strategy_class_1, strategy_class_2, rounds):
        self.strategy_class_1 = strategy_class_1
        self.strategy_class_2 = strategy_class_2
        if rounds < 1:
            raise ValueError("You can't play less than 1 round you idiot.")
        self.rounds = rounds

    def _play_round(self, strategy_1, strategy_2):
        strategy_1_move = strategy_1.get_next_move()
        strategy_2_move = strategy_2.get_next_move()

        strategy_1_result = outcomes[strategy_1_move][strategy_2_move]
        strategy_2_result = outcomes[strategy_2_move][strategy_1_move]

        strategy_1.post_move(strategy_1_move, strategy_2_move)
        strategy_2.post_move(strategy_2_move, strategy_1_move)

        print("%s (%s) - (%s) %s" % (strategy_1.name, strategy_1_move.value, strategy_2_move.value, strategy_2.name))

        return strategy_1_result, strategy_2_result

    def play(self):
        results = []
        strategy_1 = self.strategy_class_1()
        strategy_2 = self.strategy_class_2()
        for i in range(self.rounds):
            results.append(self._play_round(strategy_1, strategy_2))
        return results

    def play_entities(self, entity_1: Entity, entity_2: Entity):
        entity_1_strategy = entity_1.get_strategy_instance(entity_2)
        entity_2_strategy = entity_2.get_strategy_instance(entity_1)
        self._play_round(entity_1_strategy, entity_2_strategy)
