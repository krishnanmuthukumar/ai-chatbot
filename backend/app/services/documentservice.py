from app.storage.document_storage import DocumentStorage
from fastapi import UploadFile
import os

class DocumentService:
    def __init__(self, storage: DocumentStorage):
        self.storage = storage

    async def upload_document(self, file: UploadFile) -> str:
        """Upload a document from a multipart file upload."""
        # Read file contents
        file_contents = await file.read()
        
        # Generate document ID
        document_id = self.generate_document_id(file_contents)
        
        # Preserve file extension
        file_extension = os.path.splitext(file.filename)[1]
        document_id_with_ext = f"{document_id}{file_extension}"

        # Save the document
        self.storage.save(document_id_with_ext, file_contents)
    
        return document_id
    
    def generate_document_id(self, file_contents: bytes) -> str:
        """Generate a unique document ID based on the file contents."""
        import hashlib
        return hashlib.sha256(file_contents).hexdigest()