import os
import tempfile
from app.tools.read_award_result import read_award_result
from app.tools.read_award_result_attachment_doc import read_award_result_attachment_doc


def get_cache_path(tender_id: str, row_id: int) -> str:
    temp_dir = tempfile.gettempdir()
    temp_subdir = os.path.join(temp_dir, "mercado_publico_award_attachments")
    cache_filename = f"{tender_id}_{row_id}.pdf"
    return os.path.join(temp_subdir, cache_filename)


def test_cache():
    tender_id = "4074-24-LE19"
    
    print(f"Fetching award result for tender: {tender_id}")
    result = read_award_result.invoke({"id": tender_id})
    
    if not result.get("ok"):
        print("No award information available")
        return
    
    attachments = result.get("attachments", [])
    if not attachments:
        print("No attachments available")
        return
    
    row_id = attachments[0]["row_id"]
    cache_path = get_cache_path(tender_id, row_id)
    
    print(f"\nTesting cache for row_id={row_id}")
    print(f"Cache path: {cache_path}")
    
    cache_exists_before = os.path.exists(cache_path)
    print(f"Cache exists before first call: {cache_exists_before}")
    
    if cache_exists_before:
        print("Removing existing cache file...")
        os.remove(cache_path)
    
    print("\n--- First call (should download and cache) ---")
    result1 = read_award_result_attachment_doc.invoke({
        "id": tender_id,
        "row_id": row_id,
        "start_page": 1,
        "end_page": 2
    })
    
    cache_exists_after_first = os.path.exists(cache_path)
    cached_first = result1.get("cached", False)
    
    print(f"Result cached flag: {cached_first}")
    print(f"Cache file exists: {cache_exists_after_first}")
    print(f"File size: {result1.get('file_size', 0)} bytes")
    
    assert not cached_first, "First call should not use cache"
    assert cache_exists_after_first, "Cache file should exist after first call"
    
    print("\n--- Second call (should use cache) ---")
    result2 = read_award_result_attachment_doc.invoke({
        "id": tender_id,
        "row_id": row_id,
        "start_page": 1,
        "end_page": 2
    })
    
    cached_second = result2.get("cached", False)
    
    print(f"Result cached flag: {cached_second}")
    print(f"File size: {result2.get('file_size', 0)} bytes")
    
    assert cached_second, "Second call should use cache"
    assert result1.get("file_size") == result2.get("file_size"), "File sizes should match"
    
    print("\n✓ Cache test passed!")


if __name__ == "__main__":
    test_cache()

