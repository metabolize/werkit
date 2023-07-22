import typing as t
from ._dependency_graph import ComputeNode, DependencyGraph


class Store:
    def __init__(self, dependency_graph: DependencyGraph):
        self.dependency_graph = dependency_graph
        self.store: dict[str, t.Any] = {}

    def _assert_known_keys(self, keys: t.Iterable[str]) -> None:
        unknown_keys = set(keys) - set(self.dependency_graph.keys())
        if len(unknown_keys):
            raise KeyError(
                f"Unknown {'key' if len(unknown_keys) == 1 else 'keys'}: {', '.join(sorted(list(unknown_keys)))}"
            )

    def deserialize(self, **kwargs: t.Any) -> None:
        self._assert_known_keys(kwargs.keys())
        deserialized = {
            name: self.dependency_graph.all_nodes[name].deserialize(value)
            for name, value in kwargs.items()
        }
        self.store.update(deserialized)

    def normalize(self, **kwargs: t.Any) -> dict[str, t.Any]:
        return {
            name: self.dependency_graph.all_nodes[name].normalize(
                name=name, value=value
            )
            for name, value in kwargs.items()
        }

    def set(self, **kwargs: t.Any) -> None:
        self._assert_known_keys(kwargs.keys())
        normalized = self.normalize(**kwargs)
        self.store.update(normalized)

    def serialize(self, targets: t.Optional[t.List[str]] = None) -> dict[str, t.Any]:
        if targets is not None:
            self._assert_known_keys(targets)
            missing_keys = set(targets) - set(self.store.keys())
            if missing_keys:
                preamble = f"{'Key has' if len(missing_keys) == 1 else 'Keys have'} not been evaluated"
                raise ValueError(f"{preamble}: {', '.join(sorted(list(missing_keys)))}")
        return {
            name: self.dependency_graph.all_nodes[name].serialize_value(value)
            for name, value in self.store.items()
            if targets is None or name in targets
        }


class StateManager(Store):
    def __init__(self, instance: t.Any):
        super().__init__(
            dependency_graph=DependencyGraph.from_class(instance.__class__)
        )
        self.instance = instance

    def evaluate(
        self, targets: t.Optional[t.List[str]] = None, handle_exceptions: bool = False
    ) -> None:
        import functools
        from artifax import Artifax

        if targets is not None:
            if len(targets) == 0:
                # TODO: afx.build(targets=[]) raises an exception. This seems
                # like a bug in Artifax.
                return
            else:
                self._assert_known_keys(targets)

        def wrap_node(name: str, node: ComputeNode) -> t.Callable:
            wrapped = node.bind(self.instance)

            def wrapper(*args: list[t.Any]) -> t.Any:
                value = wrapped(*args)
                return node.normalize(name, value)

            functools.update_wrapper(wrapper, wrapped)
            return wrapper

        afx = Artifax(
            {
                name: wrap_node(name, node)
                for name, node in self.dependency_graph.compute_nodes.items()
            }
        )
        if self.store:
            afx.set(**self.store)

        if targets is None:
            self.store.update(**afx.build(targets=targets))
        else:
            values = afx.build(targets=targets)
            self.store.update(**dict(zip(targets, values)))

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
