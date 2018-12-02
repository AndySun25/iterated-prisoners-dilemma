import random

from moves import Move, outcomes, Result


class AbstractStrategy:
    name = None

    def __hash__(self):
        return self.name

    def get_next_move(self):
        raise NotImplementedError()

    def post_move(self, own_move, opponent_move):
        pass


class AlwaysCooperateStrategy(AbstractStrategy):
    name = "Always cooperate"

    def get_next_move(self):
        return Move.COOPERATE


class AlwaysDefectStrategy(AbstractStrategy):
    name = "Always defect"

    def get_next_move(self):
        return Move.DEFECT


class TitForTatStrategy(AbstractStrategy):
    name = "Tit for tat"

    def __init__(self) -> None:
        self.previous_opponent_move = Move.COOPERATE
        super().__init__()

    def get_next_move(self):
        if self.previous_opponent_move == Move.DEFECT:
            return Move.DEFECT
        else:
            return Move.COOPERATE

    def post_move(self, own_move, opponent_move):
        self.previous_opponent_move = opponent_move


class RandomStrategy(AbstractStrategy):
    name = "Random"

    def get_next_move(self):
        return Move.DEFECT if random.randint(0, 1) else Move.COOPERATE


class TitForTwoTatsStrategy(AbstractStrategy):
    name = "Tit for 2 tats"

    def __init__(self) -> None:
        self.opponent_defection_counter = 0
        super().__init__()

    def get_next_move(self):
        if self.opponent_defection_counter >= 2:
            self.opponent_defection_counter = 1
            return Move.DEFECT
        else:
            return Move.COOPERATE

    def post_move(self, own_move, opponent_move):
        if opponent_move == Move.DEFECT:
            self.opponent_defection_counter += 1

    class Memory:
        opponent_defection_counter = 0


class SuspiciousTitForTatStrategy(TitForTwoTatsStrategy):
    """
    Start by playing defect followed by TitForTwoTats.
    """
    name = "Suspicious tit for tat"

    def __init__(self) -> None:
        self.made_first_move = False
        super().__init__()

    def get_next_move(self):
        if not self.made_first_move:
            return Move.DEFECT
        else:
            return super().get_next_move()

    def post_move(self, own_move, opponent_move):
        self.made_first_move = True
        super().post_move(own_move, opponent_move)


class GenerousTitForTatStrategy(TitForTatStrategy):
    """
    Same as TFT, except that it cooperates with a probability q when the
    opponent defects.
    """
    name = "Generous tit for tat"

    def __init__(self, cooperation_probability=5) -> None:
        # Cooperation probability from 0-100 where 0 will never cooperate
        # and 100 will always cooperate.
        self.cooperation_probability = cooperation_probability
        super().__init__()

    def get_next_move(self):
        if self.previous_opponent_move == Move.DEFECT:
            if random.randint(0, 99) < self.cooperation_probability:
                return Move.COOPERATE
            return Move.DEFECT
        else:
            return Move.COOPERATE


class HardTitForTatStrategy(AbstractStrategy):
    """
    Cooperates on the first move, and defects if the opponent has defects
    on any of the previous three moves, else cooperates.
    """
    name = "Hard tit for tat"

    def __init__(self) -> None:
        self.opponent_latest_moves = (Move.COOPERATE, Move.COOPERATE, Move.COOPERATE)
        super().__init__()

    def get_next_move(self):
        if Move.DEFECT in self.opponent_latest_moves:
            return Move.DEFECT
        else:
            return Move.COOPERATE

    def post_move(self, own_move, opponent_move):
        self.opponent_latest_moves = (opponent_move,) + self.opponent_latest_moves[1:]
        super().post_move(own_move, opponent_move)


class ReverseTitForTatStrategy(TitForTatStrategy):
    """
    It does the reverse of TFT. It defects on the first move, then plays the
    reverse of the opponent’s last move.
    """
    name = "Reverse tit for tat"

    def get_next_move(self):
        if self.previous_opponent_move == Move.DEFECT:
            return Move.COOPERATE
        else:
            return Move.DEFECT


class AdaptiveStrategy(AbstractStrategy):
    """
    Starts with C,C,C,C,C,C,D,D,D,D,D and then takes choices which have given
    the best average score re-calculated after every move.
    """
    name = "Adaptive"
    initial_moves = [
        Move.COOPERATE,
        Move.COOPERATE,
        Move.COOPERATE,
        Move.COOPERATE,
        Move.COOPERATE,
        Move.DEFECT,
        Move.DEFECT,
        Move.DEFECT,
        Move.DEFECT,
        Move.DEFECT,
    ]

    def __init__(self) -> None:
        self.planned_moves = self.initial_moves.copy()
        self.move_history = []
        super().__init__()

    @property
    def average_cooperation_result(self):
        return sum(outcome.value for move, outcome in self.move_history if move == Move.COOPERATE)

    @property
    def average_defection_result(self):
        return sum(outcome.value for move, outcome in self.move_history if move == Move.DEFECT)

    def get_next_move(self):
        if self.planned_moves:
            return self.planned_moves.pop()

        if self.average_cooperation_result >= self.average_defection_result:
            return Move.COOPERATE
        else:
            return Move.DEFECT

    def post_move(self, own_move, opponent_move):
        self.move_history.append((own_move, outcomes[own_move][opponent_move]))
        super().post_move(own_move, opponent_move)


class GrimTriggerStrategy(AbstractStrategy):
    """
    Start by cooperating, continue cooperating until opponent plays defect
    after which only play defect.
    """
    name = "Grim Trigger"

    def __init__(self) -> None:
        self.opponent_has_defected = False
        super().__init__()

    def get_next_move(self):
        return Move.COOPERATE if not self.opponent_has_defected else Move.DEFECT

    def post_move(self, own_move, opponent_move):
        self.opponent_has_defected = (opponent_move == Move.DEFECT)


class PavlovStrategy(AbstractStrategy):
    """
    Start by cooperating. For every following play, play the previous move
    as long as the result of the last round was R(eward) or T(emptation).
    """
    name = "Pavlov"

    def __init__(self) -> None:
        self.last_move = Move.COOPERATE
        self.last_move_outcome = Result.R
        super().__init__()

    def get_next_move(self):
        if self.last_move_outcome in (Result.R, Result.T):
            return self.last_move
        else:
            return Move.COOPERATE if self.last_move == Move.DEFECT else Move.DEFECT

    def post_move(self, own_move, opponent_move):
        self.last_move = own_move
        self.last_move_outcome = outcomes[own_move][opponent_move]

    class Memory:
        last_move = Move.COOPERATE
        last_move_outcome = Result.R


class GradualStrategy(AbstractStrategy):
    """
    Cooperates on the first move, and cooperates as long as the opponent cooperates.
    After the first defection of the other player, it defects one time and cooperates
    two times; ... After the nth defection it reacts with n consecutive defections
    and then calms down its opponent with two cooperations.
    """
    name = "Gradual"

    def __init__(self) -> None:
        self.opponent_defection_counter = 0
        self.defection_cooldown = 0
        self.cooperation_cooldown = 0
        super().__init__()

    def get_next_move(self):
        if self.cooperation_cooldown > 0:
            self.cooperation_cooldown -= 1
            return Move.COOPERATE

        if self.defection_cooldown > 0:
            self.defection_cooldown -= 1
            if self.defection_cooldown == 0:
                self.cooperation_cooldown = 2
            return Move.DEFECT
        else:
            return Move.COOPERATE

    def post_move(self, own_move, opponent_move):
        if opponent_move == Move.DEFECT and not bool(self.defection_cooldown + self.cooperation_cooldown):
            self.opponent_defection_counter += 1
            self.defection_cooldown = self.opponent_defection_counter


class SoftMajorityStrategy(AbstractStrategy):
    """
    Cooperates on the first move, and cooperates as long as the number of times
    the opponent has cooperated is greater than or equal to the number of times
    it has defected, else it defects.
    """
    name = "Soft majority"

    def __init__(self) -> None:
        self.opponent_cooperation_counter = 0
        self.opponent_defection_counter = 0
        super().__init__()

    def get_next_move(self):
        if self.opponent_cooperation_counter >= self.opponent_defection_counter:
            return Move.COOPERATE
        else:
            return Move.DEFECT

    def post_move(self, own_move, opponent_move):
        if opponent_move == Move.COOPERATE:
            self.opponent_cooperation_counter += 1
        else:
            self.opponent_defection_counter += 1


class HardMajorityStrategy(AbstractStrategy):
    """
    Defects on the first move, and defects if the number of defections of the
    opponent is greater than or equal to the number of times it has cooperated,
    else cooperates.
    """
    name = "Hard majority"

    def __init__(self) -> None:
        self.opponent_cooperation_counter = 0
        self.opponent_defection_counter = 0
        super().__init__()

    def get_next_move(self):
        if self.opponent_defection_counter >= self.opponent_cooperation_counter:
            return Move.DEFECT
        else:
            return Move.COOPERATE

    def post_move(self, own_move, opponent_move):
        if opponent_move == Move.COOPERATE:
            self.opponent_cooperation_counter += 1
        else:
            self.opponent_defection_counter += 1


class NaiveProberStrategy(TitForTatStrategy):
    """
    Like Tit for Tat, but occasionally defects with a small probability.
    """
    name = "Naive prober"

    def __init__(self, defection_probability=5):
        # Defection probability from 0-100 where 0 will never defect
        # and 100 will always defect.
        self.defection_probability = defection_probability
        super().__init__()

    def get_next_move(self):
        if random.randint(0, 99) < self.defection_probability:
            return Move.DEFECT
        return super().get_next_move()


class RemorsefulProberStrategy(TitForTatStrategy):
    """
    Like Naive Prober, but it tries to break the series of mutual
    defections after defecting.
    """
    name = "Remorseful prober"

    def __init__(self, defection_probability=5):
        # Defection probability from 0-100 where 0 will never defect
        # and 100 will always defect.
        self.defection_probability = defection_probability
        self.has_defected = False
        super().__init__()

    def get_next_move(self):
        if self.has_defected:
            self.has_defected = False
            return Move.COOPERATE

        if random.randint(0, 99) < self.defection_probability:
            self.has_defected = True
            return Move.DEFECT
        return super().get_next_move()


class SoftGrudgerStrategy(AbstractStrategy):
    """
    Like GRIM except that the opponent is punished with D,D,D,D,C,C.
    """
    name = "Soft grudger"
    grudge_moves = [
        Move.DEFECT,
        Move.DEFECT,
        Move.DEFECT,
        Move.DEFECT,
        Move.COOPERATE,
        Move.COOPERATE,
    ]

    def __init__(self):
        self.planned_moves = []
        super().__init__()

    def get_next_move(self):
        if self.planned_moves:
            return self.planned_moves.pop(0)
        else:
            return Move.COOPERATE

    def post_move(self, own_move, opponent_move):
        if opponent_move == Move.DEFECT and not self.planned_moves:
            self.planned_moves = self.grudge_moves.copy()


class ProberStrategy(TitForTatStrategy):
    """
    Starts with D,C,C and then defects if the opponent has cooperated in the second
    and third move; otherwise, it plays TFT.
    """
    name = "Prober"

    def __init__(self):
        self.move_count = 0
        self.opponent_second_move = None
        self.opponent_third_move = None
        super().__init__()

    def get_next_move(self):
        if self.move_count == 0:
            return Move.DEFECT
        elif self.move_count == 4:
            if self.opponent_second_move == self.opponent_third_move == Move.COOPERATE:
                return Move.DEFECT
            else:
                return Move.COOPERATE
        return super().get_next_move()

    def post_move(self, own_move, opponent_move):
        self.move_count += 1

        if self.move_count == 2:
            self.opponent_second_move = opponent_move
        elif self.move_count == 3:
            self.opponent_third_move = opponent_move

        super().post_move(own_move, opponent_move)


class FirmButFairStrategy(AbstractStrategy):
    """
    Cooperates on the first move, and cooperates except after receiving a sucker payoff.
    """
    name = "Firm but fair"

    def __init__(self) -> None:
        self.last_move_outcome = Result.R
        super().__init__()

    def get_next_move(self):
        if self.last_move_outcome == Result.S:
            return Move.DEFECT
        else:
            return Move.COOPERATE

    def post_move(self, own_move, opponent_move):
        self.last_move_outcome = outcomes[own_move][opponent_move]


strategies = [v for k, v in globals().items() if isinstance(v, type)
              and issubclass(v, AbstractStrategy)
              and v != AbstractStrategy]
