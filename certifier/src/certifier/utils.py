from abc import ABC, abstractmethod
from typing import TypeVar, Set

T = TypeVar("T")


def get_all_subclasses(cls: T) -> Set[T]:
    all_subclasses = set()

    for subclass in cls.__subclasses__():
        all_subclasses.add(subclass)
        all_subclasses.update(get_all_subclasses(subclass))

    return all_subclasses


class classproperty:
    def __init__(self, method=None):
        self.fget = method

    def __get__(self, instance, cls=None):
        return self.fget(cls)

    def getter(self, method):
        self.fget = method
        return self


class Categorizable(ABC):
    @classproperty
    @abstractmethod
    def category(cls) -> str:
        pass

    @classmethod
    def for_category(cls: T, category: str) -> T:
        for subclass in get_all_subclasses(cls):
            if subclass.category == category:
                return subclass
        raise ValueError(f'Subclass for category "{category}" not found.')

    @classproperty
    def all_categories(cls) -> Set[str]:
        return {clss.category for clss in get_all_subclasses(cls)}

    def __eq__(self, other):
        return (
            isinstance(other, Categorizable)
            and self.category == other.category
        )

    def __hash__(self) -> int:
        return hash(self.category)
