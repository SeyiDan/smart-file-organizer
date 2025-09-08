#!/usr/bin/env python3
"""
Lightweight NVIDIA NIM API client.

Notes:
- Uses environment variable NVIDIA_API_KEY or config.yaml for auth
- Provides minimal methods for embeddings and multimodal endpoints
"""

import os
import json
from typing import Any, Dict, List, Optional

import urllib.request
from pathlib import Path
import base64

try:
    import yaml  # type: ignore
except Exception:
    yaml = None


class NIMClient:
    """Minimal HTTP client for NVIDIA NIM endpoints (no external deps)."""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        # Resolve from args, env, or config.yaml
        resolved_base = base_url or os.getenv("NVIDIA_NIM_BASE_URL")
        resolved_key = api_key or os.getenv("NVIDIA_API_KEY")

        if (not resolved_base or not resolved_key) and yaml is not None:
            cfg_path = self._find_config_yaml()
            if cfg_path and Path(cfg_path).exists():
                try:
                    with open(cfg_path, 'r', encoding='utf-8') as f:
                        cfg = yaml.safe_load(f) or {}
                    nim_cfg = (cfg or {}).get('nvidia_nim', {})
                    resolved_base = resolved_base or nim_cfg.get('base_url')
                    # If api_key value is like ${NVIDIA_API_KEY}, ignore and rely on env/arg
                    raw_key = nim_cfg.get('api_key')
                    if raw_key and not str(raw_key).strip().startswith('${'):
                        resolved_key = resolved_key or raw_key
                except Exception:
                    pass

        self.base_url = resolved_base or "https://integrate.api.nvidia.com/v1"
        self.api_key = resolved_key or ""

    def is_configured(self) -> bool:
        return bool(self.api_key and self.base_url)

    def _find_config_yaml(self) -> Optional[str]:
        # Look in CWD, then project root (parent of this file), then one level up
        candidates = [
            str(Path.cwd() / 'config.yaml'),
            str(Path(__file__).resolve().parents[2] / 'config.yaml') if len(Path(__file__).resolve().parents) >= 2 else None,
            str(Path(__file__).resolve().parents[1] / 'config.yaml') if len(Path(__file__).resolve().parents) >= 1 else None,
        ]
        for p in candidates:
            if p and Path(p).exists():
                return p
        return None

    def _request(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.is_configured():
            raise RuntimeError("NIM client not configured with API key/base URL")

        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        data = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", f"Bearer {self.api_key}")

        with urllib.request.urlopen(req) as resp:
            body = resp.read()
            return json.loads(body.decode("utf-8"))

    def embed(self, model: str, inputs: List[str]) -> List[List[float]]:
        """Call embeddings endpoint (OpenAI-compatible models)."""
        payload = {"model": model, "input": inputs}
        result = self._request("embeddings", payload)
        # Expected schema: { data: [ { embedding: [...] }, ... ] }
        vectors = []
        for item in result.get("data", []):
            vectors.append(item.get("embedding", []))
        return vectors

    def embed_e5(self, model: str, inputs: List[str], input_type: str) -> List[List[float]]:
        """Call e5-style embeddings that require input_type ('query' or 'passage')."""
        payload = {"model": model, "input": inputs, "input_type": input_type}
        result = self._request("embeddings", payload)
        vectors = []
        for item in result.get("data", []):
            vectors.append(item.get("embedding", []))
        return vectors

    def multimodal_analyze(self, model: str, inputs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generic multimodal invocation (vision+text)."""
        payload = {"model": model, "input": inputs}
        return self._request("chat/completions", payload)

    def chat_completion(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Text chat completion (OpenAI-style messages)."""
        payload: Dict[str, Any] = {"model": model, "messages": messages}
        payload.update(kwargs)
        return self._request("chat/completions", payload)

    def vision_chat(self, model: str, image_bytes: bytes, prompt: str, **kwargs) -> Dict[str, Any]:
        """Send an image (base64) + prompt to a vision-capable chat model."""
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        messages: List[Dict[str, Any]] = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                ],
            }
        ]
        payload: Dict[str, Any] = {"model": model, "messages": messages}
        payload.update(kwargs)
        return self._request("chat/completions", payload)


