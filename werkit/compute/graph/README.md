# Compute graph

## Example

```py
from werkit.compute.graph import bind_to_state_manager, intermediate, output

@bind_to_state_manager()
class MyComputeProcess:
    a = Input(value_type="Number")
    b = Input(value_type="Number")

    @intermediate(value_type="Number")
    def i(self, a):
        return a

    @intermediate(value_type="Number")
    def j(self, b):
        return b

    @output(value_type="Number")
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

# Serialize all output properties, automatically evaluating if needed.
serialized = compute_process.state_manager.serialize(handle_exceptions=True)

# Serialize specified properties, automatically evaluating if needed.
serialized = compute_process.serialize(targets=["i", "j", "r"], handle_exceptions=True)
```

## TODO

1. ~~JSON Schema for compute graph~~
2. Ship compute graph types in werkit npm package
3. Type checking results
4. Provide a way to serialize only the properties which have been computed
5. Error propagation
6. Serializing results vs errors
7. Proper handling of getattr bindings when computation raises an AttributeError
