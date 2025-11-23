import base64
import os
import tempfile
import time
from pydantic import BaseModel, Field
from langchain.tools import tool

from mistralai import Mistral
from mistralai.models import SDKError

from app.tools.read_supplier_attachments import (
    download_buyer_attachment_by_tender_id_and_row_id as _download_buyer_attachment
)
from app.config import settings


class ReadBuyerAttachmentDocInput(BaseModel):
    """Input schema for the read_buyer_attachment_doc tool."""
    tender_id: str = Field(
        description="The tender ID (licitación ID) from Mercado Público"
    )
    row_id: int = Field(
        description="The row ID of the attachment to read (from the attachments table)"
    )
    start_page: int = Field(
        description="Starting page number (1-indexed). REQUIRED - you must specify which page to start reading from"
    )
    end_page: int = Field(
        description="Ending page number (1-indexed, inclusive). REQUIRED - you must specify which page to end reading at"
    )


@tool(args_schema=ReadBuyerAttachmentDocInput)
def read_buyer_attachment_doc(
    tender_id: str,
    row_id: int,
    start_page: int,
    end_page: int
) -> dict:
    """Extract text from PDF using OCR. ALWAYS preview (pages 1-2) before reading more.

    Args:
        tender_id: Tender ID
        row_id: Attachment ID from read_buyer_attachments_table
        start_page: Start page (1-indexed, REQUIRED)
        end_page: End page (1-indexed inclusive, REQUIRED)

    Returns:
        dict: {text, total_pages, pages_read, file_size, success, error?}
    """
    api_key = settings.mistral_api_key
    if not api_key:
        return {
            "text": None,
            "total_pages": 0,
            "pages_read": [],
            "file_size": 0,
            "success": False,
            "error": "MISTRAL_API_KEY environment variable not set"
        }

    try:
        temp_dir = tempfile.gettempdir()
        temp_subdir = os.path.join(temp_dir, "mercado_publico_buyer_attachments")
        os.makedirs(temp_subdir, exist_ok=True)
        
        cache_filename = f"{tender_id}_{row_id}.pdf"
        cache_path = os.path.join(temp_subdir, cache_filename)
        
        cached = False
        if os.path.exists(cache_path):
            cached = True
            with open(cache_path, 'rb') as f:
                file_content = f.read()
            file_size = len(file_content)
        else:
            file_content = _download_buyer_attachment(tender_id, row_id)
            file_size = len(file_content)
            
            with open(cache_path, 'wb') as f:
                f.write(file_content)

        base64_pdf = base64.b64encode(file_content).decode('utf-8')

        # Initialize Mistral client
        client = Mistral(api_key=api_key)

        # Build pages array for Mistral API
        # Convert from 1-indexed to 0-indexed
        start = start_page - 1
        # Build range list (Mistral expects array of page numbers, 0-indexed)
        # end_page is inclusive in 1-indexed input, so we use it directly as the upper bound
        pages_to_process = list(range(start, end_page))

        # Prepare OCR request parameters
        ocr_params = {
            "model": "mistral-ocr-latest",
            "document": {
                "type": "document_url",
                "document_url": f"data:application/pdf;base64,{base64_pdf}"
            },
            "include_image_base64": False  # We only need text, not images
        }

        # Add pages parameter
        ocr_params["pages"] = pages_to_process

        # Call Mistral OCR API with retry logic for rate limits
        max_retries = 5
        base_delay = 1.0
        ocr_response = None
        
        for attempt in range(max_retries):
            try:
                ocr_response = client.ocr.process(**ocr_params)
                break
            except SDKError as e:
                http_res = e.args[1] if len(e.args) > 1 else None
                if http_res and hasattr(http_res, 'status_code') and http_res.status_code == 429:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        print(f"Rate limited, retrying in {delay:.1f}s (attempt {attempt + 1}/{max_retries})...")
                        time.sleep(delay)
                        continue
                    else:
                        raise
                else:
                    raise
        
        if ocr_response is None:
            raise Exception("Failed to get OCR response after retries")

        # Extract text from response
        extracted_text = []
        pages_read = []

        for page in ocr_response.pages:
            page_num = page.index  # 0-indexed in response
            markdown_text = page.markdown

            if markdown_text:
                extracted_text.append(f"--- Page {page_num + 1} ---\n{markdown_text}")
                pages_read.append(page_num + 1)  # Convert to 1-indexed for return

        combined_text = "\n\n".join(extracted_text)

        # Get total pages from response
        # If we requested specific pages, the total_pages is from usage_info.num_pages
        # Otherwise, it's the length of pages returned
        if hasattr(ocr_response, 'usage_info') and hasattr(ocr_response.usage_info, 'num_pages'):
            total_pages = ocr_response.usage_info.num_pages
        else:
            total_pages = len(ocr_response.pages)

        return {
            "text": combined_text,
            "total_pages": total_pages,
            "pages_read": pages_read,
            "file_size": file_size,
            "success": True,
            "cached": cached
        }

    except Exception as e:
        import traceback
        print(f"Error reading buyer attachment doc: {e}")
        traceback.print_exc()
        return {
            "text": None,
            "total_pages": 0,
            "pages_read": [],
            "file_size": 0,
            "success": False,
            "error": str(e)
        }
