import numbers
import numpy as np
from polliwog import Polyline
import vg
from ._built_in_type import BaseValue


def validate_json_value(json_value, ref):
    import os
    import simplejson as json
    from jsonschema import RefResolver, Draft7Validator

    global resolver
    if resolver is None:
        with open(
            os.path.join(os.path.dirname(__file__), "generated", "our_schema.json"), "r"
        ) as f:
            schema = json.load(f)
        resolver = RefResolver.from_schema(schema)

    return Draft7Validator({"$ref": ref}, resolver=resolver).validate(json_value)


class Point(BaseValue):
    def __init__(self, native_value):
        vg.shape.check(locals(), "native_value", (3,))
        self.value = native_value

    def to_json(self):
        return self.value.tolist()

    @classmethod
    def validate_json(cls, json_value):
        assert isinstance(json_value)

    @classmethod
    def from_json(cls, json_value):
        return cls(np.array(json_value))


class Measurement(BaseValue):
    INDICATOR_PRECISION = 4
    VALUE_PRECISION = 2

    def __init__(self, indicator, value, units):
        assert isinstance(indicator, Polyline)
        self.indicator = indicator

        assert isinstance(value, numbers.Number)
        self.value = value

        assert units in ["mm", "cm", "m", "deg"]
        self.units = units

    def to_json(self):
        return {
            "indicator": {
                "vertices": np.around(
                    self.indicator.v, self.INDICATOR_PRECISION
                ).tolist(),
                "is_closed": self.indicator.is_closed,
            },
            "value": round(self.value, self.VALUE_PRECISION),
            "units": self.units,
        }

    @classmethod
    def validate_json(cls, json_value):
        assert isinstance(json_value)

    @classmethod
    def from_json(cls, json_value):
        return cls(np.array(json_value))
