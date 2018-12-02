import random
from collections import defaultdict, Counter
from time import sleep

import strategies
from matchmaker import MatchMaker, Entity


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
        self.match_maker = MatchMaker()

    def round_robin(self, rounds=10):
        results = defaultdict(lambda: 0)
        for strategy_class_1, strategy_class_2 in round_robin_iter(self.strategy_classes):
            print("%s vs %s" % (strategy_class_1.name, strategy_class_2.name))
            match_results = self.match_maker.play_strategies(strategy_class_1, strategy_class_2, rounds)
            scores = tuple(map(enum_sum, zip(*match_results)))
            results[strategy_class_1.name] += scores[0]
            results[strategy_class_2.name] += scores[1]
            print("Results: %s vs %s\n" % scores)

        return dict(results)

    def _initialize_population(self, initial_population=10):
        population = []
        for i in range(initial_population):
            population.extend([Entity(strategy_class=strategy_class) for strategy_class in self.strategy_classes])
        return population

    def _end_round(self, population):
        for entity in population:
            # Kill the old
            if entity.age > entity.max_age:
                if not entity.has_reproduced:
                    population.append(entity.reproduce())
                population.remove(entity)
                continue

            # Kill the weak
            if entity.hit_points < 0:
                if random.randint(1, 2) % 2:
                    population.remove(entity)

            # Make babies
            if entity.age > entity.maturity_age:
                population += [entity.reproduce()]

        return population

    def ess_simulation(self):
        population = self._initialize_population()
        rnd = 0

        while True:
            rnd += 1

            print("Round: %s - Total Population %s" % (rnd, len(population)))
            round_results = defaultdict(lambda: 0)
            for entity in population:
                round_results[entity.strategy_class.name] += 1

            for strategy_name, count in sorted([(k, v) for k, v in round_results.items()], key=lambda x: x[1], reverse=True):
                print("Strategy: %s - %s" % (strategy_name, count))
            print()

            for e1, e2 in random_pair_iter(population):
                self.match_maker.play_entities(e1, e2)

            sleep(1)
            population = self._end_round(population)


if __name__ == '__main__':
    game = Game(strategies.strategies)
    game.ess_simulation()
    # results = sorted([(k, v) for k, v in game.round_robin(rounds=100).items()], key=lambda x: x[1], reverse=True)

    # print("\nScore:")
    # for result in results:
    #     print("\t%s: %s points" % result)
