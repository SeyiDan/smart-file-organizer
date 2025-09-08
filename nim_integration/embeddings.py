#!/usr/bin/env python3
"""
Embedding backends: Local (SentenceTransformers) and NVIDIA NIM.
"""

from __future__ import annotations

from typing import List, Optional

import numpy as np


class EmbeddingBackend:
    """Interface for embedding providers."""

    def embed(self, texts: List[str]) -> List[np.ndarray]:  # pragma: no cover - interface
        raise NotImplementedError


class LocalEmbeddingBackend(EmbeddingBackend):
    """Uses sentence-transformers locally."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: List[str]) -> List[np.ndarray]:
        if not texts:
            return []
        vectors = self.model.encode(texts, convert_to_numpy=True)
        # Ensure list of ndarrays
        return [np.asarray(vec) for vec in vectors]


class NIMEmbeddingBackend(EmbeddingBackend):
    """Calls NVIDIA NIM embeddings endpoint."""

    def __init__(self, model_name: str, nim_client, force_e5: bool = False, input_type: str = "passage"):
        from .nim_client import NIMClient  # local import to avoid circular

        if not isinstance(nim_client, NIMClient):
            raise TypeError("nim_client must be an instance of NIMClient")
        self.model_name = model_name
        self.client = nim_client
        self.force_e5 = force_e5 or ("e5" in model_name)
        # input_type: 'query' for queries, 'passage' for documents
        self.input_type = input_type

    def embed(self, texts: List[str]) -> List[np.ndarray]:
        if not texts:
            return []
        if self.force_e5:
            vectors = self.client.embed_e5(self.model_name, texts, self.input_type)
        else:
            vectors = self.client.embed(self.model_name, texts)
        return [np.asarray(v, dtype=float) for v in vectors]


