from ._dependency_graph import InnerNode, Input
from ._state_manager import StateManager


def bind_to_state_manager(attr_name="state_manager"):
    def decorator(cls):
        class Bound(cls):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                setattr(self, attr_name, StateManager(self))

            def __getattribute__(self, name):
                attr = object.__getattribute__(self, name)
                if isinstance(attr, Input) or isinstance(attr, InnerNode):
                    state_manager = object.__getattribute__(self, attr_name)
                    return state_manager.get(name)
                else:
                    return attr

        return Bound

    return decorator
