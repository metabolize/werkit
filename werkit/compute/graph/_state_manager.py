from ._dependencies import DependencyGraph


class StateManager:
    def __init__(self, instance):
        self.instance = instance
        self.dependency_graph = DependencyGraph(instance.__class__)
        self.store = {}

    def seed(self, **kwargs):
        unknown_keys = set(kwargs.keys()) - set(self.dependency_graph.inputs.keys())
        if len(unknown_keys):
            raise KeyError(
                f"Unknown {'key' if len(unknown_keys) == 1 else 'keys'}: {', '.join(list(unknown_keys))}"
            )
        self.store.update(kwargs)
