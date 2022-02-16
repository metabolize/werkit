from ._dependencies import DependencyGraph
from ._types import Input


class StateManager:
    def __init__(self, instance):
        self.instance = instance
        self.dependency_graph = DependencyGraph(instance.__class__)
        self._store = {}

    def seed(self, **kwargs):
        pass
