from abc import ABC
from abc import abstractmethod

from typing import List


class Instruction(ABC):
    @abstractmethod
    def exec_with_state(state):
        pass


class Stage:
    def __init__(self, instructions):
        self.instructions = instructions


class Algorithm:
    def __init__(self, stages: List[Stage]):
        self.stages = stages
