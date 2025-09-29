"""Tests for core Weavelet functionality."""

import pytest
from unittest.mock import MagicMock

from weavelet import Weave, node


def test_node_decorator_registers_function() -> None:
    """Test that @node decorator properly registers a function."""

    @node()
    def test_func(x: int) -> int:
        return x * 2

    assert hasattr(test_func, '_weavelet_node_name')
    assert test_func._weavelet_node_name == 'test_func'


def test_node_decorator_with_custom_name() -> None:
    """Test that @node decorator accepts custom name."""

    @node(name="custom_name")
    def test_func(x: int) -> int:
        return x * 2

    assert test_func._weavelet_node_name == 'custom_name'


def test_weave_params_add_and_get() -> None:
    """Test parameter storage functionality."""
    weave = Weave()
    weave.params.add("test_param", "test_value")

    assert weave.params.get("test_param") == "test_value"
    assert weave.params.get("nonexistent") is None
    assert weave.params.get("nonexistent", "default") == "default"


def test_weave_include_module() -> None:
    """Test including a module with nodes."""
    weave = Weave()

    # Create a mock module with a decorated function
    mock_module = MagicMock()

    @node()
    def mock_func(x: int) -> int:
        return x * 2

    # Set up the mock module to return our function
    mock_module.__dict__ = {'mock_func': mock_func}
    type(mock_module).mock_func = mock_func

    # Mock inspect.getmembers to return our function
    import inspect
    original_getmembers = inspect.getmembers

    def mock_getmembers(module):
        return [('mock_func', mock_func)]

    inspect.getmembers = mock_getmembers

    try:
        weave.include(mock_module)
        assert 'mock_func' in weave._nodes
    finally:
        inspect.getmembers = original_getmembers


def test_simple_dag_execution() -> None:
    """Test execution of simple DAG with dependencies."""
    weave = Weave()

    @node()
    def step1(input_value: int) -> int:
        return input_value * 2

    @node()
    def step2(step1: int) -> int:
        return step1 + 10

    # Manually add nodes (simulating include)
    weave._nodes['step1'] = step1
    weave._nodes['step2'] = step2

    weave.params.add("input_value", 5)

    result = weave.run("step2")
    assert result == 20  # (5 * 2) + 10


def test_caching_prevents_recomputation() -> None:
    """Test that results are cached and functions aren't called multiple times."""
    weave = Weave()
    call_count = 0

    @node()
    def expensive_func(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * 2

    weave._nodes['expensive_func'] = expensive_func
    weave.params.add("x", 5)

    # First call
    result1 = weave.run("expensive_func")
    assert result1 == 10
    assert call_count == 1

    # Second call should use cache
    result2 = weave.run("expensive_func")
    assert result2 == 10
    assert call_count == 1  # Should not increment


def test_missing_parameter_raises_error() -> None:
    """Test that missing parameters raise appropriate error."""
    weave = Weave()

    @node()
    def needs_param(missing_param: str) -> str:
        return missing_param.upper()

    weave._nodes['needs_param'] = needs_param

    with pytest.raises(ValueError, match="Missing parameter 'missing_param'"):
        weave.run("needs_param")


def test_missing_node_raises_error() -> None:
    """Test that running nonexistent node raises error."""
    weave = Weave()

    with pytest.raises(ValueError, match="Node 'nonexistent' not found"):
        weave.run("nonexistent")


def test_clear_cache() -> None:
    """Test cache clearing functionality."""
    weave = Weave()

    @node()
    def test_func(x: int) -> int:
        return x * 2

    weave._nodes['test_func'] = test_func
    weave.params.add("x", 5)

    # Execute and cache result
    result = weave.run("test_func")
    assert result == 10
    assert 'test_func' in weave._cache

    # Clear cache
    weave.clear_cache()
    assert 'test_func' not in weave._cache