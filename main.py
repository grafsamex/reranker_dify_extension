"""
BGE Reranker Extension for Dify
Main entry point for the reranker plugin
"""

import os
import logging
import requests
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class BGERerankerProvider:
    """
    Reranker Provider for Dify
    This class registers the reranker as a model provider in Dify
    """
    
    def __init__(self):
        """Initialize the reranker provider"""
        self.name = "BGE Reranker v2 m3"
        self.display_name = "BGE Reranker"
        self.model_name = "BAAI/bge-reranker-v2-m3"
        self.description = "High-performance document reranking using BAAI/bge-reranker-v2-m3"
        
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get provider information for Dify registration
        
        Returns:
            Dictionary with provider metadata
        """
        return {
            "name": self.name,
            "display_name": self.display_name,
            "model_name": self.model_name,
            "description": self.description,
            "type": "reranker",
            "supports_gpu": True,
            "max_documents": 1000,
            "max_query_length": 512,
            "max_document_length": 512
        }
    
    def validate_credentials(self, credentials: Dict[str, Any]) -> bool:
        """
        Validate provider credentials (API URL)
        
        Args:
            credentials: Dictionary with api_url and other settings
            
        Returns:
            True if credentials are valid
        """
        api_url = credentials.get("api_url", "")
        if not api_url or not isinstance(api_url, str):
            return False
        
        # Try to check health endpoint
        try:
            health_url = urljoin(api_url.rstrip('/') + '/', 'health')
            response = requests.get(health_url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available models from this provider
        
        Returns:
            List of model dictionaries
        """
        return [{
            "model": self.model_name,
            "name": self.display_name,
            "model_type": "reranker",
            "provider": self.name
        }]

class BGEReranker:
    """BGE Reranker client for Dify integration"""
    
    def __init__(
        self, 
        api_url: str = None, 
        timeout: int = 30, 
        top_k: int = 5,
        input_format: str = "auto",
        output_format: str = "standard"
    ):
        """
        Initialize the BGE Reranker client
        
        Args:
            api_url: Base URL of the reranker API service
            timeout: Request timeout in seconds
            top_k: Default number of top results to return
            input_format: Format for input field name - "passages", "documents", or "auto" (auto-detect)
            output_format: Format for output - "standard" (with index) or "simple" (without index)
        """
        self.api_url = api_url or os.getenv("RERANKER_API_URL", "http://localhost:8009")
        self.timeout = timeout
        self.top_k = top_k
        self.input_format = input_format.lower() if input_format else "auto"
        self.output_format = output_format.lower() if output_format else "standard"
        self.rerank_endpoint = urljoin(self.api_url.rstrip('/') + '/', 'rerank')
        self.health_endpoint = urljoin(self.api_url.rstrip('/') + '/', 'health')
        
        # Remove trailing slash
        self.api_url = self.api_url.rstrip('/')
        
        # Validate input format
        if self.input_format not in ["passages", "documents", "auto"]:
            logger.warning(f"Unknown input_format '{input_format}', using 'auto'")
            self.input_format = "auto"
        
        # Validate output format
        if self.output_format not in ["standard", "simple"]:
            logger.warning(f"Unknown output_format '{output_format}', using 'standard'")
            self.output_format = "standard"
        
    def health_check(self) -> Dict[str, Any]:
        """
        Check if the reranker service is healthy
        
        Returns:
            Dictionary with health status information
        """
        try:
            response = requests.get(self.health_endpoint, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def rerank(
        self,
        query: str,
        documents: List[str],
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Rerank documents by relevance to the query
        
        Args:
            query: Search query string
            documents: List of document texts to rerank
            top_k: Number of top results to return (overrides default)
            
        Returns:
            List of reranked documents with scores, sorted by relevance
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        if not documents:
            raise ValueError("Documents list cannot be empty")
        
        if not isinstance(documents, list):
            raise TypeError("Documents must be a list")
        
        top_k = top_k or self.top_k
        
        # Determine input field name based on format setting
        if self.input_format == "auto":
            # Try to detect: default to "passages" (our API format)
            input_field = "passages"
        elif self.input_format == "documents":
            input_field = "documents"
        else:
            input_field = "passages"
        
        # Prepare request payload with configurable field name
        payload = {
            "query": query,
            input_field: documents,
            "top_k": min(top_k, len(documents))
        }
        
        # Some APIs use "top_n" instead of "top_k"
        # We'll try both if needed, but start with "top_k"
        
        try:
            # Make request to reranker API
            response = requests.post(
                self.rerank_endpoint,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Extract and format results based on output format
            reranked_docs = []
            for item in result.get("results", []):
                doc_result = {
                    "document": item.get("document", ""),
                    "score": item.get("score", 0.0)
                }
                
                # Add index only if standard format is requested
                if self.output_format == "standard":
                    doc_result["index"] = item.get("index", -1)
                
                reranked_docs.append(doc_result)
            
            return reranked_docs
            
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout after {self.timeout} seconds")
            raise Exception(f"Reranker service timeout after {self.timeout} seconds")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise Exception(f"Failed to connect to reranker service: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise


def rerank(
    query: str,
    documents: List[str],
    config: Optional[Dict[str, Any]] = None,
    model: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Main entry point for Dify extension
    
    This function is called by Dify when the reranker is used
    
    Args:
        query: Search query string
        documents: List of document texts to rerank
        config: Optional configuration dictionary with:
            - api_url: URL of the reranker service
            - timeout: Request timeout in seconds
            - top_k: Number of top results to return
            - input_format: "passages", "documents", or "auto" (default: "auto")
            - output_format: "standard" (with index) or "simple" (without index) (default: "standard")
        model: Optional model name (for compatibility with Dify model selection)
            
    Returns:
        List of reranked documents with scores
    """
    # Extract configuration
    config = config or {}
    api_url = config.get("api_url", os.getenv("RERANKER_API_URL", "http://localhost:8009"))
    timeout = config.get("timeout", 30)
    top_k = config.get("top_k", 5)
    input_format = config.get("input_format", "auto")
    output_format = config.get("output_format", "standard")
    
    # Initialize reranker client with format settings
    reranker = BGEReranker(
        api_url=api_url, 
        timeout=timeout, 
        top_k=top_k,
        input_format=input_format,
        output_format=output_format
    )
    
    # Perform reranking
    results = reranker.rerank(query, documents, top_k=top_k)
    
    return results


def get_reranker_provider():
    """
    Get reranker provider instance for Dify registration
    
    Returns:
        BGERerankerProvider instance
    """
    return BGERerankerProvider()


def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalize configuration
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Validated configuration dictionary
    """
    validated = {}
    
    # Validate api_url
    api_url = config.get("api_url", os.getenv("RERANKER_API_URL", "http://localhost:8009"))
    if not isinstance(api_url, str) or not api_url.strip():
        raise ValueError("api_url must be a non-empty string")
    validated["api_url"] = api_url.strip().rstrip('/')
    
    # Validate timeout
    timeout = config.get("timeout", 30)
    try:
        timeout = int(timeout)
        if timeout < 1 or timeout > 300:
            raise ValueError("timeout must be between 1 and 300 seconds")
    except (ValueError, TypeError):
        raise ValueError("timeout must be a valid integer")
    validated["timeout"] = timeout
    
    # Validate top_k
    top_k = config.get("top_k", 5)
    try:
        top_k = int(top_k)
        if top_k < 1 or top_k > 100:
            raise ValueError("top_k must be between 1 and 100")
    except (ValueError, TypeError):
        raise ValueError("top_k must be a valid integer")
    validated["top_k"] = top_k
    
    # Validate input_format
    input_format = config.get("input_format", "auto")
    if input_format not in ["passages", "documents", "auto"]:
        logger.warning(f"Invalid input_format '{input_format}', using 'auto'")
        input_format = "auto"
    validated["input_format"] = input_format
    
    # Validate output_format
    output_format = config.get("output_format", "standard")
    if output_format not in ["standard", "simple"]:
        logger.warning(f"Invalid output_format '{output_format}', using 'standard'")
        output_format = "standard"
    validated["output_format"] = output_format
    
    return validated

