"""
References:

https://github.com/ivankorobkov/python-inject
https://github.com/illuin-tech/opyoid
https://github.com/ets-labs/python-dependency-injector
"""


class MyComputeProcess:
    a = Input(_type="Number")
    b = Input(_type="Number")

    @intermediate(_type="Number")
    def i(self, a):
        return a

    @intermediate(_type="Number")
    def j(self, b):
        return b

    @output(_type="Number")
    def r(self, i, j):
        return i + j


compute_process = MyComputeProcess()

# Inject dependencies.
inject(compute_process, a=1, b=2)

# Manually trigger evaluation of properties, storing and optionally raising exceptions.
evaluate(compute_process, ["r"], handle_exceptions=False)

# Read properties, automatically evaluating if needed. Raises exceptions.
print(compute_process.r)
print(compute_process.i)

# Serialize all output properties, automatically evaluating if needed.
serialized = serialize(compute_process, handle_exceptions=True)

# Serialize specified properties, automatically evaluating if needed.
serialized = serialize(compute_process, ["i", "j", "r"], handle_exceptions=True)
