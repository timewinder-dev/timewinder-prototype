from abc import ABC
from abc import abstractmethod


class OpcodeStoreInterface(ABC):
    @abstractmethod
    def debug_print(self):
        pass

    @abstractmethod
    def resolve_var(self, varname: str):
        pass

    @abstractmethod
    def resolve_getattr(self, base, attr):
        pass

    @abstractmethod
    def resolve_setattr(self, base, attr, val):
        pass

    @abstractmethod
    def store_fast(self, name, val):
        pass

    @abstractmethod
    def call_function(self, name, args):
        pass

    @abstractmethod
    def on_yield(self, val):
        pass
