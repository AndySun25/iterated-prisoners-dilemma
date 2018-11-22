import random
from collections import defaultdict

import strategies
from match import Match


def enum_sum(enums):
    return sum(enum.value for enum in enums)


def round_robin_iter(items):
    for i, item in enumerate(items):
        for opponent in items[i+1:]:
            yield item, opponent


def random_pair_iter(items):
    cp = list(items).copy()

    while len(cp) >= 2:
        item = cp.pop()
        opponent = cp.pop(random.randint(0, len(cp) - 1))
        yield item, opponent


class Game:
    def __init__(self, strategy_classes):
        self.strategy_classes = strategy_classes

    def round_robin(self, rounds=10):
        results = defaultdict(lambda: 0)
        for strategy_class_1, strategy_class_2 in round_robin_iter(self.strategy_classes):
            print("%s vs %s" % (strategy_class_1.name, strategy_class_2.name))
            match = Match(strategy_class_1, strategy_class_2, rounds)
            match_results = match.play()
            scores = tuple(map(enum_sum, zip(*match_results)))
            results[strategy_class_1.name] += scores[0]
            results[strategy_class_2.name] += scores[1]
            print("Results: %s vs %s\n" % scores)

        return dict(results)


if __name__ == '__main__':
    game = Game(strategies.strategies)
    results = sorted([(k, v) for k, v in game.round_robin(rounds=10).items()], key=lambda x: x[1], reverse=True)

    print("\nScore:")
    for result in results:
        print("\t%s: %s points" % result)
