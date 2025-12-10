"""BGE Reranker Extension for Dify."""

__version__ = "0.1.0"
__author__ = "BGE Reranker Team"

# Public surface of the package is the plugin runner.
from .main import plugin

__all__ = ["plugin", "__version__", "__author__"]
