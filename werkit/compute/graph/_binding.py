import typing as t
from ._dependency_graph import ComputeNode, Input
from ._state_manager import StateManager


def bind_state_manager(attr_name="state_manager"):
    def decorator(cls):
        class Bound(cls):
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
