import typing as t
from ._dependency_graph import DependencyGraph


class StateManager:
    def __init__(self, instance: t.Any):
        self.instance = instance
        self.dependency_graph = DependencyGraph(instance.__class__)
        self.store: t.Dict = {}

    def _assert_known_keys(self, keys: t.Iterable[str]) -> None:
        unknown_keys = set(keys) - set(self.dependency_graph.keys())
        if len(unknown_keys):
            raise KeyError(
                f"Unknown {'key' if len(unknown_keys) == 1 else 'keys'}: {', '.join(sorted(list(unknown_keys)))}"
            )

    def deserialize(self, **kwargs: t.Dict) -> None:
        self._assert_known_keys(kwargs.keys())
        deserialized = {
            name: self.dependency_graph.all_nodes[name].deserialize(value)
            for name, value in kwargs.items()
        }
        self.store.update(deserialized)

    def coerce(self, **kwargs: t.Dict) -> t.Dict:
        return {
            name: self.dependency_graph.all_nodes[name].coerce(name=name, value=value)
            for name, value in kwargs.items()
        }

    def set(self, **kwargs: t.Dict) -> None:
        self._assert_known_keys(kwargs.keys())
        coerced = self.coerce(**kwargs)
        self.store.update(coerced)

    def evaluate(
        self, targets: t.List[str] = None, handle_exceptions: bool = False
    ) -> None:
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
        coerced = self.coerce(**afx._result)
        self.store.update(coerced)

    def serialize(self, targets: t.List[str] = None) -> t.Dict:
        self.evaluate(targets=targets)

        return {
            name: self.dependency_graph.all_nodes[name].serialize_value(value)
            for name, value in self.store.items()
            if targets is None or name in targets
        }

    def get(self, name: str) -> t.Any:
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
