from moves import outcomes


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
