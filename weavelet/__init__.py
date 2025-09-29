"""
Weavelet - A library for managing function calls in specific order.

A simple DAG-based function orchestration library similar to Apache Hamilton
but simpler without unnecessary 3rd party dependencies.
"""

from .core import Weave, node

__version__ = "0.0.1"
__all__ = ["node", "Weave"]
