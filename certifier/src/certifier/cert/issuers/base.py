from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from certifier.utils import Categorizable

ContextType = TypeVar("ContextType")
ConfigType = TypeVar("ConfigType")


class Issuer(Categorizable, ABC, Generic[ContextType, ConfigType]):
    @classmethod
    @abstractmethod
    def issue(cls, context: ContextType, config: ConfigType) -> None:
        pass
