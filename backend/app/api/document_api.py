
from asyncio.log import logger
from app.dependencies.document_dependencies import get_document_service, get_document_storage
from app.config import get_settings
from fastapi import APIRouter, UploadFile, File

router = APIRouter()

@router.post("/documents")
async def upload_document(file: UploadFile = File(...)):
    logger.info(f"Uploading document: {file.filename}")
    settings = get_settings()
    service = get_document_service(get_document_storage(settings))
    document_id = await service.upload_document(file)
    logger.info(f"Document uploaded with ID: {document_id}")
    return {"document_id": document_id}