import functools
from ._types import assert_valid_type


class BaseNode:
    def __init__(self, method, _type):
        self.method = method
        assert_valid_type(_type)
        self._type = _type

    def __get__(self, instance, type=None):
        return functools.partial(self, instance)

    def __call__(self, *args, **kwargs):
        return self.method(*args, **kwargs)

    def as_native(self):
        return {"type": self._type}


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
