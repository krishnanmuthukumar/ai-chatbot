from app.services.documentservice import DocumentService
from app.storage.document_storage import DocumentStorage
from app.storage.local_doc_storage import LocalDocStorage
from app.config import Settings
from fastapi import Depends

def get_document_storage(settings: Settings) -> DocumentStorage:
    if settings.DOCUMENT_STORAGE_TYPE == "local":
        return LocalDocStorage(settings)
    else:
        raise ValueError(f"Unsupported document storage type: {settings.DOCUMENT_STORAGE_TYPE}")

def get_document_service(storage: DocumentStorage = Depends(get_document_storage)) -> DocumentService:
    return DocumentService(storage)