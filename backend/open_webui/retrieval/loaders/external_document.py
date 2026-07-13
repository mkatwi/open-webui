import requests
import logging, os
from typing import Iterator, List, Union

from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from open_webui.env import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["RAG"])


def _document_from_response(document: dict) -> Document:
    if not isinstance(document, dict):
        raise Exception("Error loading document: Unable to parse content")

    page_content = document.get("page_content") or ""
    if not isinstance(page_content, str):
        page_content = str(page_content)

    metadata = document.get("metadata") or {}
    if not isinstance(metadata, dict):
        metadata = {}

    return Document(page_content=page_content, metadata=metadata)


class ExternalDocumentLoader(BaseLoader):
    def __init__(
        self,
        file_path,
        url: str,
        api_key: str,
        mime_type=None,
        **kwargs,
    ) -> None:
        self.url = url
        self.api_key = api_key

        self.file_path = file_path
        self.mime_type = mime_type

    def load(self) -> List[Document]:
        with open(self.file_path, "rb") as f:
            data = f.read()

        headers = {}
        if self.mime_type is not None:
            headers["Content-Type"] = self.mime_type

        if self.api_key is not None:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            headers["X-Filename"] = os.path.basename(self.file_path)
        except:
            pass

        url = self.url
        if url.endswith("/"):
            url = url[:-1]

        try:
            response = requests.put(f"{url}/process", data=data, headers=headers)
        except Exception as e:
            log.error(f"Error connecting to endpoint: {e}")
            raise Exception(f"Error connecting to endpoint: {e}")

        if response.ok:

            response_data = response.json()
            if response_data:
                if isinstance(response_data, dict):
                    return [_document_from_response(response_data)]
                elif isinstance(response_data, list):
                    documents = []
                    for document in response_data:
                        documents.append(_document_from_response(document))
                    return documents
                else:
                    raise Exception("Error loading document: Unable to parse content")

            else:
                raise Exception("Error loading document: No content returned")
        else:
            raise Exception(
                f"Error loading document: {response.status_code} {response.text}"
            )
