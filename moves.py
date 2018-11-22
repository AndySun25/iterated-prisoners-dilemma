from enum import Enum


class Move(Enum):
    COOPERATE = "cooperate"
    DEFECT = "defect"


class Result(Enum):
    # T as in (T)emptation payoff
    T = 5
    # R as in cooperation (R)eward
    R = 3
    # P as in (P)unishment
    P = 1
    # S as in (S)uckaaaaaaa
    S = 0


ess_result_map = {
    Result.T: 1,
    Result.R: 1,
    Result.P: -1,
    Result.S: -1,
}


outcomes = {
    Move.COOPERATE: {
        Move.COOPERATE: Result.R,
        Move.DEFECT: Result.S,
    },
    Move.DEFECT: {
        Move.COOPERATE: Result.T,
        Move.DEFECT: Result.P,
    }
}
