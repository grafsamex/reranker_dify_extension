import json
import logging
from typing import Optional
from urllib.parse import urljoin

import requests
from dify_plugin import RerankModel
from dify_plugin.entities.model import (
    AIModelEntity,
    FetchFrom,
    I18nObject,
    ModelPropertyKey,
    ModelType,
)
from dify_plugin.entities.model.rerank import RerankDocument, RerankResult
from dify_plugin.errors.model import (
    CredentialsValidateFailedError,
    InvokeAuthorizationError,
    InvokeBadRequestError,
    InvokeConnectionError,
    InvokeError,
    InvokeRateLimitError,
    InvokeServerUnavailableError,
)

logger = logging.getLogger(__name__)


class BGERerankModel(RerankModel):
    """
    Model class for BGE Reranker v2 m3 model.
    """

    def _invoke(
        self,
        model: str,
        credentials: dict,
        query: str,
        documents: list[str],
        score_threshold: Optional[float] = None,
        top_n: Optional[int] = None,
        user: Optional[str] = None,
    ) -> RerankResult:
        """
        Invoke rerank model

        :param model: model name
        :param credentials: model credentials
        :param query: search query
        :param documents: docs for reranking
        :param score_threshold: score threshold
        :param top_n: top n documents to return
        :param user: unique user id
        :return: rerank result
        """
        if len(documents) == 0:
            return RerankResult(model=model, docs=[])

        headers = {"Content-Type": "application/json"}
        api_url = credentials.get("api_url", "").rstrip("/")
        timeout = credentials.get("timeout", 30)
        top_k = top_n or credentials.get("top_k", 5)
        input_format = credentials.get("input_format", "auto")
        
        # Determine input field name
        if input_format == "documents":
            input_field = "documents"
        else:
            input_field = "passages"
        
        endpoint_url = urljoin(api_url + "/", "rerank")

        payload = {
            "query": query,
            input_field: documents,
            "top_k": min(top_k, len(documents))
        }

        try:
            response = requests.post(
                endpoint_url, 
                headers=headers, 
                json=payload, 
                timeout=timeout
            )
            response.raise_for_status()
            response_data = response.json()

            rerank_documents = []
            results = response_data.get("results", [])
            
            if top_n is not None:
                results = results[:top_n]

            for item in results:
                index = item.get("index", -1)
                # Compatible with different response formats
                if "document" in item:
                    text = item["document"]
                else:
                    text = documents[index] if index >= 0 and index < len(documents) else ""
                
                score = item.get("score", item.get("relevance_score", 0.0))
                
                # Apply score threshold filter
                if score_threshold is None or score >= score_threshold:
                    rerank_document = RerankDocument(
                        index=index,
                        text=text,
                        score=score
                    )
                    rerank_documents.append(rerank_document)

            return RerankResult(model=model, docs=rerank_documents)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise InvokeAuthorizationError(str(e))
            elif e.response.status_code == 429:
                raise InvokeRateLimitError(str(e))
            elif e.response.status_code >= 500:
                raise InvokeServerUnavailableError(str(e))
            else:
                raise InvokeBadRequestError(str(e))
        except requests.exceptions.ConnectionError:
            raise InvokeConnectionError("Connection error occurred")
        except requests.exceptions.Timeout:
            raise InvokeConnectionError("Request timeout")
        except Exception as e:
            logger.error(f"Unexpected error in BGE rerank: {str(e)}")
            raise InvokeError(f"Unexpected error: {str(e)}")

    def validate_credentials(self, model: str, credentials: dict) -> None:
        """
        Validate model credentials

        :param model: model name
        :param credentials: model credentials
        :return:
        """
        try:
            api_url = credentials.get("api_url", "").rstrip("/")
            health_url = urljoin(api_url + "/", "health")
            timeout = credentials.get("timeout", 30)
            
            response = requests.get(health_url, timeout=min(timeout, 5))
            response.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            raise CredentialsValidateFailedError(
                f"An error occurred during credentials validation: status code {ex.response.status_code}: {ex.response.text}"
            )
        except Exception as ex:
            raise CredentialsValidateFailedError(
                f"An error occurred during credentials validation: {str(ex)}"
            )

    def get_customizable_model_schema(
        self, model: str, credentials: dict
    ) -> AIModelEntity:
        """
        generate custom model entities from credentials
        """
        entity = AIModelEntity(
            model=model,
            label=I18nObject(en_US=model),
            model_type=ModelType.RERANK,
            fetch_from=FetchFrom.CUSTOMIZABLE_MODEL,
            model_properties={
                ModelPropertyKey.CONTEXT_SIZE: int(
                    credentials.get("context_size", 512)
                ),
            },
        )
        return entity

    @property
    def _invoke_error_mapping(self) -> dict[type[InvokeError], list[type[Exception]]]:
        """
        Map model invoke error to unified error
        """
        return {
            InvokeAuthorizationError: [requests.exceptions.InvalidHeader],
            InvokeBadRequestError: [
                requests.exceptions.HTTPError,
                requests.exceptions.InvalidURL,
            ],
            InvokeRateLimitError: [requests.exceptions.RetryError],
            InvokeServerUnavailableError: [
                requests.exceptions.ConnectionError,
                requests.exceptions.HTTPError,
            ],
            InvokeConnectionError: [
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ReadTimeout,
            ],
        }
