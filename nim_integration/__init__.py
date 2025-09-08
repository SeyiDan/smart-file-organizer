"""
NVIDIA NIM integration adapters for the Smart Semantic File Organizer.

Provides:
- NIMClient: minimal HTTP client for NVIDIA NIM endpoints
- Embedding backends: Local and NIM-based providers
"""

from .nim_client import NIMClient  # noqa: F401
from .embeddings import (  # noqa: F401
    EmbeddingBackend,
    LocalEmbeddingBackend,
    NIMEmbeddingBackend,
)


