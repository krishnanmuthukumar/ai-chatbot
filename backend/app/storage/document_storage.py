from abc import ABC, abstractmethod

class DocumentStorage(ABC):
    @abstractmethod
    def save(self, document_id: str, file: bytes) -> None:
        pass

    @abstractmethod
    def get(self, document_id: str) -> bytes:
        pass

    @abstractmethod
    def delete(self, document_id: str) -> None:
        pass

    @abstractmethod
    def exists(self, document_id: str) -> bool:
        pass