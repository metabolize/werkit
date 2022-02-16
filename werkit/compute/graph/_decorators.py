from ._types import assert_valid_type


class BaseNode:
    def __init__(self, method, _type):
        import inspect

        self.method = method

        assert_valid_type(_type)
        self._type = _type

        self.dependencies = [x for x in inspect.signature(method).parameters.keys()][1:]

    def __get__(self, instance, type=None):
        import functools

        return functools.partial(self, instance)

    def __call__(self, *args, **kwargs):
        return self.method(*args, **kwargs)

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
