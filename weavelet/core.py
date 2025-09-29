"""Core functionality for Weavelet."""

import inspect
from collections import defaultdict, deque
from collections.abc import Callable
from functools import wraps
from types import ModuleType
from typing import Any

# Global registry to store all decorated functions
_NODE_REGISTRY: dict[str, Callable[..., Any]] = {}


def node(name: str | None = None) -> Callable[[Callable[..., Any]], Any]:
    """
    Decorator to register a function as a node in the DAG.

    Args:
        name: Optional name for the node. If not provided, uses function name.
    """

    def decorator(func: Callable[..., Any]) -> Any:
        node_name = name or func.__name__
        _NODE_REGISTRY[node_name] = func

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        # Add custom attribute for node identification - type: ignore for mypy
        wrapper._weavelet_node_name = node_name  # type: ignore[attr-defined]
        return wrapper

    return decorator


class Params:
    """Parameter storage for the Weave execution."""

    def __init__(self) -> None:
        self._params: dict[str, Any] = {}

    def add(self, name: str, value: Any) -> None:
        """Add a parameter value."""
        self._params[name] = value

    def get(self, name: str, default: Any = None) -> Any:
        """Get a parameter value."""
        return self._params.get(name, default)

    def update(self, params: dict[str, Any]) -> None:
        """Update multiple parameters at once."""
        self._params.update(params)


class Weave:
    """Main orchestration class for executing DAG of functions."""

    def __init__(self) -> None:
        self.params = Params()
        self._cache: dict[str, Any] = {}
        self._nodes: dict[str, Callable[..., Any]] = {}

    def include(self, module: ModuleType) -> None:
        """
        Include all nodes from a module.

        Args:
            module: Python module containing decorated functions
        """
        # Get all functions from the module that are registered as nodes
        for _name, obj in inspect.getmembers(module):
            if hasattr(obj, "_weavelet_node_name"):
                node_name: str = obj._weavelet_node_name
                if node_name in _NODE_REGISTRY:
                    self._nodes[node_name] = _NODE_REGISTRY[node_name]

    def _get_function_signature(self, func: Callable[..., Any]) -> dict[str, Any]:
        """Get function parameter names and types."""
        sig = inspect.signature(func)
        return {
            "params": list(sig.parameters.keys()),
            "return_annotation": sig.return_annotation,
        }

    def _build_dependency_graph(self) -> dict[str, list[str]]:
        """Build dependency graph based on function signatures."""
        graph: dict[str, list[str]] = defaultdict(list)

        for node_name, func in self._nodes.items():
            sig_info = self._get_function_signature(func)
            for param in sig_info["params"]:
                # If parameter matches another node's name, it's a dependency
                if param in self._nodes:
                    graph[node_name].append(param)

        return dict(graph)

    def _topological_sort(self, target_node: str) -> list[str]:
        """
        Perform topological sort to determine execution order.
        Only includes nodes needed to compute the target.
        """
        graph = self._build_dependency_graph()

        # Find all nodes needed to compute target
        needed_nodes: set[str] = set()
        stack = [target_node]

        while stack:
            current = stack.pop()
            if current in needed_nodes:
                continue
            needed_nodes.add(current)

            # Add dependencies to stack
            for dep in graph.get(current, []):
                if dep not in needed_nodes:
                    stack.append(dep)

        # Perform topological sort on needed nodes only
        in_degree: dict[str, int] = defaultdict(int)
        for node in needed_nodes:
            for dep in graph.get(node, []):
                if dep in needed_nodes:
                    in_degree[node] += 1

        queue: deque[str] = deque(
            [node for node in needed_nodes if in_degree[node] == 0]
        )
        result: list[str] = []

        while queue:
            current = queue.popleft()
            result.append(current)

            # Reduce in-degree for dependent nodes
            for node in needed_nodes:
                if current in graph.get(node, []):
                    in_degree[node] -= 1
                    if in_degree[node] == 0:
                        queue.append(node)

        if len(result) != len(needed_nodes):
            raise ValueError("Circular dependency detected in the DAG")

        return result

    def _execute_node(self, node_name: str) -> Any:
        """Execute a single node with proper parameter injection."""
        if node_name in self._cache:
            return self._cache[node_name]

        func = self._nodes[node_name]
        sig_info = self._get_function_signature(func)

        # Prepare arguments
        kwargs: dict[str, Any] = {}
        for param in sig_info["params"]:
            if param in self._cache:
                # Use result from another node
                kwargs[param] = self._cache[param]
            elif self.params.get(param) is not None:
                # Use parameter value
                kwargs[param] = self.params.get(param)
            else:
                raise ValueError(f"Missing parameter '{param}' for node '{node_name}'")

        # Execute function
        result = func(**kwargs)

        # Cache result
        self._cache[node_name] = result

        return result

    def run(self, target: str) -> Any:
        """
        Execute the DAG to compute the target node.

        Args:
            target: Name of the target node to compute

        Returns:
            Result of the target node execution
        """
        if target not in self._nodes:
            available_nodes = list(self._nodes.keys())
            raise ValueError(
                f"Node '{target}' not found. Available nodes: {available_nodes}"
            )

        # Get execution order
        execution_order = self._topological_sort(target)

        # Execute nodes in order
        for node_name in execution_order:
            self._execute_node(node_name)

        return self._cache[target]

    def clear_cache(self) -> None:
        """Clear the execution cache."""
        self._cache.clear()
