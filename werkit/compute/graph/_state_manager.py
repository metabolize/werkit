from ._dependencies import DependencyGraph


class StateManager:
    def __init__(self, instance):
        self.instance = instance
        self.dependency_graph = DependencyGraph(instance.__class__)
        self.store = {}

    def _assert_known_keys(self, keys):
        unknown_keys = set(keys) - set(self.dependency_graph.keys())
        if len(unknown_keys):
            raise KeyError(
                f"Unknown {'key' if len(unknown_keys) == 1 else 'keys'}: {', '.join(sorted(list(unknown_keys)))}"
            )

    def seed(self, **kwargs):
        self._assert_known_keys(kwargs.keys())
        self.store.update(kwargs)

    def evaluate(self, targets=None, handle_exceptions=False):
        from artifax import Artifax

        if targets is not None:
            self._assert_known_keys(targets)

        afx = Artifax(
            {
                name: self.dependency_graph.compute_nodes[name].bind(self.instance)
                for name in self.dependency_graph.compute_nodes.keys()
            }
        )
        if self.store:
            afx.set(**self.store)
        afx.build(targets=targets)
        # TODO: `afx.build()` should always return an object.
        self.store.update(afx._result)

    def serialize(self, targets=None, handle_exceptions=False):
        self.evaluate(targets=targets)

        if targets is None:
            return self.store
        else:
            return {k: self.store[k] for k in targets}

    def get(self, name):
        self._assert_known_keys([name])

        try:
            return self.store[name]
        except KeyError:
            pass

        if name in self.dependency_graph.inputs:
            raise KeyError(f"Input has not been set: {name}")

        if name in self.dependency_graph.compute_nodes.keys():
            self.evaluate(targets=[name])

        return self.store[name]
