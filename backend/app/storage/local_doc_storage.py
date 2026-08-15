from app.storage.document_storage import DocumentStorage
from app.config import Settings
from os import path, makedirs, remove

class LocalDocStorage(DocumentStorage):

    def __init__(self, settings: Settings):
        self.storage_path = settings.DOCUMENT_STORAGE_PATH
        makedirs(self.storage_path, exist_ok=True)

    def save(self, document_id: str, file: bytes) -> None:
        file_path = f"{self.storage_path}/{document_id}"
        with open(file_path, 'wb') as f:
            f.write(file)

    def get(self, document_id: str) -> bytes:
        file_path = f"{self.storage_path}/{document_id}"
        with open(file_path, 'rb') as f:
            return f.read()

    def delete(self, document_id: str) -> None:
        file_path = f"{self.storage_path}/{document_id}"
        remove(file_path)

    def exists(self, document_id: str) -> bool:
        file_path = f"{self.storage_path}/{document_id}"
        return path.exists(file_path)
