from dataclasses import dataclass

from enum import Enum


class PauseReason(Enum):
    NORMAL = 0
    PC_JUMPED = 1
    YIELD = 2
    DONE = 3


class Fairness(Enum):
    NORMAL = 0
    WEAKLY_FAIR = 1
    FAIR = 2
    IMMEDIATE = 3


@dataclass
class Continue:
    kind: PauseReason = PauseReason.NORMAL
    yield_msg: str = ""
    fairness: Fairness = Fairness.NORMAL
