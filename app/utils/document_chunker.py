from typing import List

def chunk_by_paragraphs(text: str, max_chunk_size: int = 1000) -> List[str]:
    """Chunk text by paragraphs, respecting document structure"""
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        # If adding this paragraph would exceed the chunk size, finalize current chunk
        if len(current_chunk) + len(paragraph) > max_chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = paragraph
        else:
            # Add paragraph to current chunk
            if current_chunk:
                current_chunk += '\n\n' + paragraph
            else:
                current_chunk = paragraph
    
    # Add the last chunk if it exists
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def chunk_by_sentences(text: str, max_chunk_size: int = 1000) -> List[str]:
    """Chunk text by sentences for more granular splitting"""
    import re
    sentences = re.split(r'[.!?]+', text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # If adding this sentence would exceed the chunk size, finalize current chunk
        if len(current_chunk) + len(sentence) > max_chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            # Add sentence to current chunk
            if current_chunk:
                current_chunk += '. ' + sentence
            else:
                current_chunk = sentence
    
    # Add the last chunk if it exists
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def chunk_document(text: str, method: str = "paragraph", max_chunk_size: int = 1000) -> List[str]:
    """Intelligently chunk document based on specified method"""
    if method == "paragraph":
        return chunk_by_paragraphs(text, max_chunk_size)
    elif method == "sentence":
        return chunk_by_sentences(text, max_chunk_size)
    else:
        # Default to fixed-size splitting with overlap
        chunks = []
        for i in range(0, len(text), max_chunk_size):
            chunk = text[i:i + max_chunk_size]
            chunks.append(chunk)
        return chunks