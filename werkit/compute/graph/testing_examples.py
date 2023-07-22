import typing as t
from . import (
    CustomType,
    DependencyGraphJSONType,
    Input,
    bind_state_manager,
    intermediate,
    output,
)


@bind_state_manager()
class MyComputeProcess:
    a = Input(value_type=int)
    b = Input(value_type=int)

    @intermediate(value_type=int)
    def i(self, a: int) -> int:
        return a

    @intermediate(value_type=int)
    def j(self, b: int) -> int:
        return b

    @output(value_type=int)
    def r(self, i: int, j: int) -> int:
        return i + j


EXPECTED_INPUTS = ["a", "b"]
EXPECTED_INTERMEDIATES = ["i", "j"]
EXPECTED_OUTPUT = "r"

EXPECTED_SERIALIZED_DEPENDENCY_GRAPH: DependencyGraphJSONType = {
    "schemaVersion": 1,
    "inputs": {"a": {"valueType": "number"}, "b": {"valueType": "number"}},
    "intermediates": {
        "i": {"valueType": "number", "dependencies": ["a"]},
        "j": {"valueType": "number", "dependencies": ["b"]},
    },
    "outputs": {"r": {"valueType": "number", "dependencies": ["i", "j"]}},
}


class MyComputeProcessSubclass(MyComputeProcess):
    pass


class MyRaisingComputeProcess(MyComputeProcess):
    @output(value_type=int)
    def s(self) -> int:
        raise ValueError("Whoops")

    @output(value_type=int)
    def t(self) -> int:
        raise ValueError("Whoops")


class MyWronglyTypedComputeProcess(MyComputeProcess):
    @output(value_type=int)
    def s(self) -> bool:
        return False


class MyModel:
    def __init__(self, title: str, description: str, count: int):
        if title is None or description is None or count is None:
            raise ValueError("All properties are required")
        self.title = title
        self.description = description
        self.count = count


class MyModelType(CustomType[MyModel]):
    @classmethod
    def name(cls) -> str:
        return "MyModel"

    @classmethod
    def normalize(cls, value: t.Any) -> MyModel:
        if not isinstance(value, MyModel):
            raise ValueError(
                f"Can't normalize {type(value).__name__} to {cls.__name__}"
            )
        return value

    @classmethod
    def serialize(self, value: MyModel) -> t.Any:
        return {
            "title": value.title,
            "description": value.description,
            "count": value.count,
        }

    @classmethod
    def deserialize(self, json_data: t.Any) -> MyModel:
        json_data = t.cast(dict, json_data)
        return MyModel(**json_data)


class Vector3(CustomType[tuple]):
    DECIMALS = 2

    @classmethod
    def normalize(cls, value: t.Any) -> tuple:
        if not isinstance(value, tuple):
            raise ValueError(
                f"Can't normalize {type(value).__name__} to {cls.__name__}"
            )
        elif not len(value) == 3:
            raise ValueError("Excepted tuple to have length 3")
        return tuple(round(coord, cls.DECIMALS) for coord in value)

    @classmethod
    def serialize(self, value: tuple) -> t.Any:
        return list(value)

    @classmethod
    def deserialize(self, json_data: t.Any) -> tuple:
        json_data = t.cast(list, json_data)
        return tuple(json_data)


class MyComputeProcessWithCustomType(MyComputeProcess):
    @output(value_type=MyModelType)
    def thing(self) -> MyModel:
        return MyModel(
            title="Example title", description="Example description", count=25
        )

    @output(value_type=Vector3)
    def other_thing(self) -> tuple:
        return (1.5151, 2.5151, 3.5151)

    @output(value_type=str)
    def further_derived_thing(self, other_thing: tuple) -> str:
        return str(other_thing)
