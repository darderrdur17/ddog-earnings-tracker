from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

import requests

from .config import Settings


class HttpError(RuntimeError):
    pass


class JsonHttpClient:
    """GET JSON with retries, exponential backoff, and optional disk cache."""

    def __init__(self, settings: Settings, session: requests.Session | None = None):
        self.settings = settings
        self.session = session or requests.Session()
        self.settings.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_json(self, url: str, *, cache: bool = True) -> Any:
        cache_path = self._cache_path(url)
        if cache and self._fresh(cache_path):
            return json.loads(cache_path.read_text())

        last_error: Exception | None = None
        delay = 1.0
        for attempt in range(1, self.settings.http_retries + 1):
            try:
                response = self.session.get(
                    url,
                    headers={"User-Agent": self.settings.user_agent},
                    timeout=self.settings.http_timeout,
                )
                if response.status_code == 404:
                    raise HttpError(f"404 for {url}")
                if response.status_code in {429, 500, 502, 503, 504}:
                    retry_after = response.headers.get("Retry-After")
                    if retry_after and retry_after.isdigit():
                        delay = max(delay, float(retry_after))
                    raise HttpError(f"{response.status_code} for {url}")
                response.raise_for_status()
                payload = response.json()
                if cache:
                    cache_path.write_text(json.dumps(payload))
                return payload
            except HttpError as exc:
                last_error = exc
                if "404" in str(exc) or attempt == self.settings.http_retries:
                    break
                time.sleep(delay)
                delay = min(delay * 2, 16.0)
            except (requests.RequestException, ValueError, OSError) as exc:
                last_error = exc
                if attempt == self.settings.http_retries:
                    break
                time.sleep(delay)
                delay = min(delay * 2, 16.0)
        raise HttpError(f"Failed GET {url}: {last_error}") from last_error

    def get_text(self, url: str, *, cache: bool = True) -> str:
        cache_path = self._cache_path(url, suffix=".txt")
        if cache and self._fresh(cache_path):
            return cache_path.read_text()

        last_error: Exception | None = None
        delay = 1.0
        for attempt in range(1, self.settings.http_retries + 1):
            try:
                response = self.session.get(
                    url,
                    headers={"User-Agent": self.settings.user_agent},
                    timeout=self.settings.http_timeout,
                )
                if response.status_code == 404:
                    raise HttpError(f"404 for {url}")
                if response.status_code in {429, 500, 502, 503, 504}:
                    retry_after = response.headers.get("Retry-After")
                    if retry_after and retry_after.isdigit():
                        delay = max(delay, float(retry_after))
                    raise HttpError(f"{response.status_code} for {url}")
                response.raise_for_status()
                payload = response.text
                if cache:
                    cache_path.write_text(payload)
                return payload
            except HttpError as exc:
                last_error = exc
                if "404" in str(exc) or attempt == self.settings.http_retries:
                    break
                time.sleep(delay)
                delay = min(delay * 2, 16.0)
            except (requests.RequestException, OSError) as exc:
                last_error = exc
                if attempt == self.settings.http_retries:
                    break
                time.sleep(delay)
                delay = min(delay * 2, 16.0)
        raise HttpError(f"Failed GET {url}: {last_error}") from last_error

    def _cache_path(self, url: str, suffix: str = ".json") -> Path:
        digest = hashlib.sha256(url.encode()).hexdigest()[:24]
        return self.settings.cache_dir / f"{digest}{suffix}"

    def _fresh(self, path: Path) -> bool:
        if not path.exists():
            return False
        age = time.time() - path.stat().st_mtime
        return age < self.settings.cache_ttl_seconds
