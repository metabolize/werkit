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

        graph = {}
        graph.update(
            **{
                k: getattr(self.instance, k)
                for k in list(self.dependency_graph.intermediates.keys())
                + list(self.dependency_graph.outputs.keys())
            },
        )

        afx = Artifax(graph)
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
