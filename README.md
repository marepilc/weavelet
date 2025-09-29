# Weavelet

A library for managing function calls in specific order, to avoid code repeating. Similar to Apache Hamilton but simpler without 3rd party dependencies if not needed.

## Features

- **Simple DAG orchestration**: Build execution graphs based on function signatures
- **Decorator-based**: Register functions as nodes using the `@node()` decorator
- **Cross-module support**: Nodes can be spread across multiple files
- **Parameter injection**: Automatic dependency resolution and parameter passing
- **Result caching**: Avoid recomputing expensive operations
- **Pure Python**: No external dependencies for core functionality

## Quick Start

### Installation

```bash
pip install weavelet
```

### Basic Usage

Create nodes in any Python file:

```python
# a_nodes.py
from weavelet import node

@node()
def auth_token(api_key: str) -> str:
    return f"Bearer {api_key}"

@node()
def user_profile(auth_token: str, user_id: int) -> dict:
    return {"id": user_id, "name": "Ala"}

@node()
def make_greeting(user_profile: dict) -> str:
    return f"Hello, {user_profile['name']}!"
```

Execute the DAG:

```python
# main.py
from weavelet import Weave
import a_nodes

weave = Weave()
weave.include(a_nodes)
weave.params.add("api_key", "xyz")
weave.params.add("user_id", 128)

result = weave.run("make_greeting")  # -> "Hello, Ala!"
print(result)
```

## How it Works

Weavelet automatically builds a DAG based on function signatures:
- Function parameters that match other node names become dependencies
- Parameters not matching node names are injected from `weave.params`
- Execution order is determined through topological sorting
- Results are cached to avoid redundant computation

## Requirements

- Python >=3.12
- No external dependencies for core functionality

## Development

Uses `uv` as package manager with TDD approach.