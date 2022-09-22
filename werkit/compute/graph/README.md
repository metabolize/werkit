# Compute graph

## Example

```py
from werkit.compute.graph import bind_state_manager, intermediate, output

@bind_state_manager()
class MyComputeProcess:
    a = Input(value_type=int)
    b = Input(value_type=int)

    @intermediate(value_type=int)
    def i(self, a):
        return a

    @intermediate(value_type=int)
    def j(self, b):
        return b

    @output(value_type=int)
    def r(self, i, j):
        return i + j


compute_process = MyComputeProcess()

# Inject dependencies.
compute_process.state_manager.set(a=1, b=2)

# Manually trigger evaluation of properties, storing and optionally raising exceptions.
compute_process.state_manager.evaluate(targets=["r"], handle_exceptions=False)

# Read properties, automatically evaluating if needed. Raises exceptions.
print(compute_process.r)
print(compute_process.i)

# Serialize the evaluated properties.
serialized = compute_process.state_manager.serialize(handle_exceptions=True)

# Serialize a specified subset of the evaluated properties.
serialized = compute_process.state_manager.serialize(targets=["r"], handle_exceptions=True)
```

## TODO

1. ~~JSON Schema for compute graph~~
2. ~~Ship compute graph types in werkit npm package~~
3. ~~Type checking results~~
4. ~~Provide a way to serialize only the properties which have been computed~~
5. Error propagation
6. Serializing results vs errors
7. Proper handling of getattr bindings when computation raises an AttributeError
8. Document custom types
