"""
Provider Registry for Dify
This module registers the reranker as a model provider in Dify
"""

from typing import Dict, Any, List
from .main import BGERerankerProvider, rerank


def register_reranker_provider() -> Dict[str, Any]:
    """
    Register the reranker provider in Dify
    
    This function is called by Dify to discover and register the provider
    
    Returns:
        Dictionary with provider registration information
    """
    provider = BGERerankerProvider()
    
    return {
        "provider_name": provider.name,
        "provider_type": "reranker",
        "provider_class": "main:BGERerankerProvider",
        "models": provider.get_models(),
        "credentials_schema": {
            "type": "object",
            "properties": {
                "api_url": {
                    "type": "string",
                    "title": "API URL",
                    "description": "URL of the reranker API service",
                    "default": "http://localhost:8009"
                },
                "timeout": {
                    "type": "integer",
                    "title": "Timeout",
                    "description": "Request timeout in seconds",
                    "default": 30,
                    "minimum": 1,
                    "maximum": 300
                },
                "top_k": {
                    "type": "integer",
                    "title": "Top K",
                    "description": "Number of top results to return",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 100
                },
                "input_format": {
                    "type": "string",
                    "title": "Input Format",
                    "description": "Input field name: 'passages' (default), 'documents' (Dify), or 'auto' (auto-detect)",
                    "default": "auto",
                    "enum": ["passages", "documents", "auto"]
                },
                "output_format": {
                    "type": "string",
                    "title": "Output Format",
                    "description": "Output format: 'standard' (with index) or 'simple' (without index)",
                    "default": "standard",
                    "enum": ["standard", "simple"]
                }
            },
            "required": ["api_url"]
        },
        "rerank_function": rerank
    }


# Export for Dify discovery
__all__ = ["register_reranker_provider"]

