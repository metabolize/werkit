import typing as t
from typing_extensions import Protocol

from ._dependency_graph import ComputeNode, Input
from ._state_manager import StateManager


Unbound = t.TypeVar("Unbound")


class DefaultStateManager(Protocol):
    @property
    def state_manager(self) -> StateManager:
        ...


class WithDefaultStateManager(Unbound, DefaultStateManager):
    pass


@t.overload
def bind_state_manager() -> t.Callable[[Unbound], WithDefaultStateManager]:
    ...


@t.overload
def bind_state_manager(attr_name: str) -> t.Callable[[Unbound], Unbound]:
    ...


def bind_state_manager(
    attr_name: str = "state_manager",
) -> t.Union[
    t.Callable[[Unbound], WithDefaultStateManager], t.Callable[[Unbound], Unbound]
]:
    def decorator(cls: type[t.Any]) -> WithDefaultStateManager:
        class Bound(cls, DefaultStateManager):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                setattr(self, attr_name, StateManager(self))

            def __getattribute__(self, name: str) -> t.Any:
                attr = object.__getattribute__(self, name)
                if isinstance(attr, Input) or isinstance(attr, ComputeNode):
                    state_manager = object.__getattribute__(self, attr_name)
                    return state_manager.get(name)
                else:
                    return attr

        return Bound

    return decorator
