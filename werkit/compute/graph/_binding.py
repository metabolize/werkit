import typing as t

from ._dependency_graph import ComputeNode, Input
from ._state_manager import StateManager


# This decorator is hard to type, so we provide a protcol which can be used with
# `t.cast()`.

# https://github.com/python/typing/issues/213
# https://stackoverflow.com/a/75101725/893113
# https://stackoverflow.com/a/74041065/893113
# https://github.com/python/mypy/issues/3135


class DefaultStateManagerProtocol(t.Protocol):
    @property
    def state_manager(self) -> StateManager:  # pragma: no cover
        ...


T = t.TypeVar("T")


def bind_state_manager(
    attr_name: str = "state_manager",
) -> t.Callable[[type[T]], type[T]]:
    def decorator(cls):  # type: ignore[no-untyped-def]
        class Bound(cls):  # type: ignore[no-untyped-def]
            def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
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
