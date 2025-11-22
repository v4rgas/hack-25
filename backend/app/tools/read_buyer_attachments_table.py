from pydantic import BaseModel, Field
from langchain.tools import tool

from app.tools.read_supplier_attachments import read_buyer_attachments_table as _read_buyer_attachments_table


class ReadBuyerAttachmentsTableInput(BaseModel):
    """Input schema for the read_buyer_attachments_table tool."""
    tender_id: str = Field(
        description="The tender ID (licitación ID) from Mercado Público to retrieve attachments for"
    )


@tool(args_schema=ReadBuyerAttachmentsTableInput)
def read_buyer_attachments_table(tender_id: str) -> list:
    """List all tender attachments with metadata.

    Args:
        tender_id: Tender ID from Mercado Público

    Returns:
        list: [[id, file_name, type, description, file_size, uploaded_at], ...]
    """
    return _read_buyer_attachments_table(tender_id)
