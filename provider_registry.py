"""
Legacy provider registry kept for compatibility.

The current plugin is fully described by `manifest.yaml` and the provider/model
definitions under `provider/` and `models/`. This module now only exports a
no-op helper to avoid import errors in older code paths.
"""

from typing import Dict, Any


def register_reranker_provider() -> Dict[str, Any]:
    """
    Legacy shim for old discovery flows.

    Returns minimal metadata without touching runtime classes, so imports stay
    safe even though Dify now relies on manifest-based discovery.
    """
    return {
        "provider_name": "bge_reranker",
        "provider_type": "reranker",
        "provider_class": "provider.bge_reranker:BGERerankerProvider",
        "note": "Use manifest.yaml for actual registration.",
    }


__all__ = ["register_reranker_provider"]
