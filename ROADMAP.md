# Weavelet Development Roadmap to v1.0

## Vision
Weavelet aims to be the simplest and most intuitive DAG orchestration library for Python, focusing on automatic dependency resolution and execution deduplication. The core principle: **when multiple nodes depend on the same upstream node, execute it once and reuse the result**.

## Current State (v0.0.1)

### ✅ Implemented Features
- **Core DAG Engine**: Function signature-based dependency resolution
- **Decorator API**: Simple `@node()` decorator for function registration
- **Parameter Injection**: Automatic parameter resolution from external inputs
- **Result Caching**: Avoid recomputation of expensive operations
- **Module Inclusion**: Cross-module node discovery and registration
- **Execution Engine**: Topological sorting and optimized execution order
- **Error Handling**: Clear error messages for missing dependencies/parameters
- **Type Safety**: Full mypy compliance with strict typing
- **Test Coverage**: 97% test coverage with comprehensive test suite

### 🔧 Development Infrastructure
- Modern Python packaging (pyproject.toml, uv)
- Quality tools (pytest, mypy, ruff)
- TDD-ready setup with CLAUDE.md guidelines

## Roadmap to v1.0

### Phase 1: v0.1.0 - Production-Ready Core
**Target: 4-6 weeks**
**Focus**: Deliver a solid, usable library for async workflows with excellent error handling and introspection.

#### 🚀 Async Support (Critical)
- [ ] **Async node execution**: Support for `async def` decorated functions
- [ ] **Mixed sync/async DAGs**: Seamless integration of sync and async nodes
- [ ] **Concurrent execution**: Parallel execution of independent async nodes
- [ ] **Async parameter injection**: Handle async parameter resolution

#### 🏷️ Advanced Return Types (Critical)
- [ ] **Annotated return types**: Support `Annotated[tuple[T1, T2], "name1", "name2"]` for multi-output nodes
- [ ] **Named output resolution**: Allow nodes to depend on named outputs from multi-output nodes
- [ ] **Type-safe unpacking**: Ensure mypy compliance for multi-output patterns

#### 🔍 Introspection (Essential for usability)
- [ ] **DAG visualization**: Generate visual representations (text/graphviz) of execution graphs
- [ ] **Execution context in errors**: Show DAG path when errors occur

#### 📊 Error Handling (Critical for correctness)
- [ ] **Circular dependency detection**: Clear error messages with suggested fixes
- [ ] **Better error messages**: Include node names and dependency chains in errors

### Phase 2: v0.2.0 - Developer Experience
**Target: 3-4 weeks**
**Focus**: Enhanced debugging, profiling, and quality-of-life improvements.

#### 🔍 Advanced Introspection
- [ ] **Execution profiling**: Built-in timing and performance metrics per node
- [ ] **Debug mode**: Verbose logging with execution traces
- [ ] **Dependency analysis**: Tools to analyze and optimize DAG structure

#### 🧪 Testing & Development
- [ ] **Testing utilities**: Helpers for mocking nodes and testing workflows
- [ ] **Jupyter integration**: Better notebook experience with rich output
- [ ] **Hot reloading**: Development mode with auto-reload on code changes

### Phase 3: v0.3.0 - Production Features
**Target: 3-4 weeks**
**Focus**: Scalability and production-readiness.

#### 🏗️ Scalability
- [ ] **Multiprocessing**: Distribute execution across CPU cores
- [ ] **Memory management**: Smart memory usage and garbage collection
- [ ] **Resource limits**: CPU/memory limits per node

#### 🔧 Configuration
- [ ] **Configuration files**: YAML/JSON configuration support
- [ ] **Environment variables**: Environment-based parameter injection
- [ ] **CLI interface**: Command-line tool for running workflows

### Phase 4+: Future Enhancements
**Post-v0.3.0 - As needed based on user feedback**

#### 🎯 Advanced Execution Patterns
- [ ] **Conditional execution**: Execute nodes based on runtime conditions
- [ ] **Dynamic DAGs**: Generate DAG structure at runtime
- [ ] **Retry mechanisms**: Automatic retry with backoff strategies
- [ ] **Checkpoint/Resume**: Save and resume long-running workflows

#### 🐻‍❄️ Domain-Specific Support (As Needed)
- [ ] **Polars integration**: Schema validation and lazy evaluation
- [ ] **Image processing**: PIL/Pillow and OpenCV support
- [ ] **File operations**: Path handling and file watching
- [ ] **Cloud storage**: S3, GCS, Azure integration

#### 🔌 Ecosystem & Extensions
- [ ] **Plugin architecture**: Extensible plugin system
- [ ] **Documentation generation**: Auto-generate workflow docs
- [ ] **Distributed computing**: Dask/Ray integration

## Example Use Cases

### 1. Async API Orchestration (v0.1)
```python
@node()
async def fetch_user_data(user_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        return await client.get(f"/api/users/{user_id}").json()

@node()
async def fetch_user_posts(user_id: str) -> list[dict]:
    async with httpx.AsyncClient() as client:
        return await client.get(f"/api/posts?user={user_id}").json()

@node()
async def fetch_user_comments(user_id: str) -> list[dict]:
    async with httpx.AsyncClient() as client:
        return await client.get(f"/api/comments?user={user_id}").json()

@node()
def create_user_profile(
    user_data: dict,
    posts: list[dict],
    comments: list[dict]
) -> dict:
    # fetch_user_data, fetch_user_posts, and fetch_user_comments
    # all run concurrently - user_id is only computed once!
    return {
        "user": user_data,
        "content": {
            "posts": posts,
            "comments": comments
        }
    }

# Execute efficiently with automatic concurrency
weave = Weave()
profile = weave.execute("create_user_profile", user_id="123")
```

### 2. Multi-Output Nodes with Annotated (v0.1)
```python
from typing import Annotated

@node()
def expensive_analysis(data: list[float]) -> Annotated[
    tuple[float, float, list[float]],
    "mean",
    "std",
    "outliers"
]:
    # Expensive computation done once
    mean = sum(data) / len(data)
    std = (sum((x - mean) ** 2 for x in data) / len(data)) ** 0.5
    outliers = [x for x in data if abs(x - mean) > 2 * std]
    return mean, std, outliers

@node()
def create_summary(mean: float, std: float) -> dict:
    # Automatically receives named outputs from expensive_analysis
    return {"mean": mean, "std": std}

@node()
def flag_outliers(outliers: list[float]) -> list[str]:
    # Also receives named output - expensive_analysis runs only once!
    return [f"ALERT: {x}" for x in outliers]

# Both create_summary and flag_outliers depend on expensive_analysis
# but it executes only once, outputs are automatically distributed
```

### 3. Data Processing Pipeline
```python
@node()
def load_data(file_path: str) -> dict:
    with open(file_path) as f:
        return json.load(f)

@node()
def clean_data(raw_data: dict) -> dict:
    return {k: v for k, v in raw_data.items() if v is not None}

@node()
def calculate_metrics(clean_data: dict) -> dict:
    return {
        "count": len(clean_data),
        "total": sum(clean_data.values())
    }

@node()
def generate_report(metrics: dict, clean_data: dict) -> str:
    # clean_data is reused from earlier execution
    return f"Report: {metrics}, Sample: {list(clean_data.items())[:5]}"
```

## Success Metrics for v0.1

### Core Functionality
- [ ] **Async execution**: Seamlessly mix sync and async nodes
- [ ] **Concurrency**: Independent async nodes run in parallel automatically
- [ ] **Multi-output nodes**: Clean API using `Annotated` for multiple named outputs
- [ ] **Error handling**: Circular dependency detection with helpful messages
- [ ] **Visualization**: Generate DAG graphs to understand execution flow

### Code Quality
- [ ] **Type safety**: 100% mypy strict compliance
- [ ] **Test coverage**: Maintain >95% coverage
- [ ] **Documentation**: Clear examples for all v0.1 features
- [ ] **Performance**: Minimal overhead compared to direct function calls

### Developer Experience
- [ ] **Simplicity**: Adding `@node()` is the only boilerplate needed
- [ ] **Debuggability**: Clear error messages with execution context
- [ ] **Usability**: Works with any Python types (no special requirements)

---

**Next Steps**: Start with Phase 1 (v0.1.0) development, focusing on async support and `Annotated` return types as the foundation for a production-ready library.