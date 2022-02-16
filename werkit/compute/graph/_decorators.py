import inspect
from ._types import assert_valid_type, Input


class BaseNode:
    def __init__(self, method, _type):
        self.method = method

        assert_valid_type(_type)
        self._type = _type

        self.dependencies = [x for x in inspect.signature(method).parameters.keys()][1:]

    def bind(self, instance):
        import functools

        return functools.partial(self.method, instance)

    def as_native(self):
        return {"type": self._type, "dependencies": self.dependencies}


class Intermediate(BaseNode):
    pass


class Output(BaseNode):
    pass


def intermediate(_type: str):
    def decorator(method):
        return Intermediate(method, _type)

    return decorator


def output(_type: str):
    def decorator(method):
        return Output(method, _type)

    return decorator


class Bound:
    def __getattribute__(self, name):
        attr = object.__getattribute__(self, name)
        # import pdb; pdb.set_trace()
        if isinstance(attr, Input) or isinstance(attr, BaseNode):
            return object.__getattribute__(self, "state_manager").get(name)
        else:
            return attr
