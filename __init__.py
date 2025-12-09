"""
BGE Reranker Extension for Dify
"""

__version__ = "1.0.0"
__author__ = "BGE Reranker Team"

from .main import (
    rerank, 
    BGEReranker, 
    BGERerankerProvider,
    validate_config,
    get_reranker_provider
)

__all__ = [
    "rerank", 
    "BGEReranker", 
    "BGERerankerProvider",
    "validate_config",
    "get_reranker_provider"
]

