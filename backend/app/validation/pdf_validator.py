import fitz
from app.config import get_settings
from fastapi import HTTPException, status, UploadFile

def validate_pdf(file :UploadFile) -> None:
    """
    Validate if the uploaded file is a PDF.
        """

    if file.content_type != get_settings().ALLOWED_CONTENT_TYPE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail=f"Invalid content type '{file.content_type}'. Only PDF files are allowed.")
    file.file.seek(0, 2)  # Move the cursor to the end of the file
    file_size = file.file.tell()  # Get the current position (which is the file size)
    file.file.seek(0)  # Reset the cursor to the beginning of the file

    if file_size > get_settings().MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail=f"File size exceeds the maximum limit of {get_settings().MAX_FILE_SIZE / (1024 * 1024)} MB.")

    header = file.file.read(5)
    file.file.seek(0)  # Reset the cursor to the beginning of the file

    if header != b'%PDF-':
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Uploaded file is not a valid PDF. The file header does not match the expected PDF signature.")

    try:
        file_bytes = file.file.read()
        file.file.seek(0)  # Reset the cursor to the beginning of the file

        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            _ = doc.page_count  # Accessing page_count to ensure the PDF is valid
            if doc.page_count == 0:
                raise ValueError("PDF has no pages.")
            
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"Uploaded file is not a valid PDF. Error: {str(e)}")