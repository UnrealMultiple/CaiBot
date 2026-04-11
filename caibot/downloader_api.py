"""
Downloader API client.
All requests are made against the base URL configured in ``config.downloader_url``
(env var ``DOWNLOADER_URL``).
"""

import re
from html.parser import HTMLParser
from typing import Optional
from urllib.parse import quote, urlparse, parse_qs

import httpx

from caibot import config

def _resolve_url(path: str) -> str:
    """Build an absolute URL by joining *path* onto the configured base URL."""
    base = config.downloader_url.rstrip('/')
    if not path.startswith('/'):
        path = '/' + path
    return base + path


class _DirectoryTableParser(HTMLParser):
    """Parse an nginx/Apache-style HTML directory listing into structured data."""

    def __init__(self) -> None:
        super().__init__()
        self._in_tr: bool = False
        self._in_td: bool = False
        self._current_row: list[tuple[str, Optional[str]]] = []
        self._current_cell: str = ''
        self._current_href: Optional[str] = None
        self.items: list[dict] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        attrs_dict = dict(attrs)
        if tag == 'tr':
            self._in_tr = True
            self._current_row = []
            self._current_href = None
        elif tag == 'td' and self._in_tr:
            self._in_td = True
            self._current_cell = ''
            self._current_href = None
        elif tag == 'a' and self._in_td:
            self._current_href = attrs_dict.get('href', '')

    def handle_endtag(self, tag: str) -> None:
        if tag == 'tr':
            self._process_row()
            self._in_tr = False
        elif tag == 'td' and self._in_tr:
            self._current_row.append((self._current_cell.strip(), self._current_href))
            self._in_td = False

    def handle_data(self, data: str) -> None:
        if self._in_td:
            self._current_cell += data

    def _process_row(self) -> None:
        if len(self._current_row) < 3:
            return

        name, href = self._current_row[0]
        # Skip parent directory and hidden entries
        if not name or name == '..' or name.startswith('.'):
            return

        href = href or ''
        size_text = self._current_row[1][0]
        last_modified_text = self._current_row[2][0]
        is_directory = href.endswith('/')

        self.items.append({
            'name': name,
            'size': None if size_text == '-' else size_text or None,
            'lastModified': None if last_modified_text == '-' else last_modified_text or None,
            'isDirectory': is_directory,
        })


def parse_directory_listing(html: str) -> list[dict]:
    """Parse HTML directory listing into a list of ``{name, size, lastModified, isDirectory}`` dicts."""
    parser = _DirectoryTableParser()
    parser.feed(html)
    return parser.items

async def submit_download(url_or_id: str) -> dict:
    """Submit a mod URL or ID to the download queue.

    POST /api/downloader/queue
    """
    async with httpx.AsyncClient() as client:
        res = await client.post(
            _resolve_url('/api/downloader/queue'),
            json={'UrlOrId': url_or_id},
        )

    if res.status_code != 200:
        text = res.text[:100] if res.text else ''
        raise RuntimeError(f'HTTP {res.status_code}' + (f': {text}' if text else ''))

    data: dict = {}
    try:
        data = res.json()
    except Exception:
        pass

    if data.get('isSuccess') is False:
        raise RuntimeError(data.get('message') or 'Queue request failed')

    return data


async def get_mod_versions(mod_id: str) -> Optional[list[dict]]:
    """Get available versions of a mod.

    GET /depots/{id}/
    Returns ``None`` if the mod is not found (404).
    """
    async with httpx.AsyncClient() as client:
        res = await client.get(_resolve_url(f'/depots/{quote(mod_id, safe="")}/'))

    if res.status_code == 404:
        return None
    if res.status_code != 200:
        raise RuntimeError(f'HTTP {res.status_code}')

    return parse_directory_listing(res.text)


async def get_mod_files(mod_id: str, version: str) -> Optional[list[dict]]:
    """Get files for a specific version of a mod.

    GET /depots/{id}/{version}/
    Returns ``None`` if not found (404).
    """
    async with httpx.AsyncClient() as client:
        res = await client.get(
            _resolve_url(f'/depots/{quote(mod_id, safe="")}/{quote(version, safe="")}/'),
        )

    if res.status_code == 404:
        return None
    if res.status_code != 200:
        raise RuntimeError(f'HTTP {res.status_code}')

    return parse_directory_listing(res.text)


def get_download_url(
    mod_id: str,
    version: Optional[str],
    file_name: str,
    sub_path: list[str] | None = None,
) -> str:
    """Return the direct download URL for a specific mod file.

    Optionally place the file inside *sub_path* sub-folders.
    """
    sub_path = sub_path or []
    segments = [quote(str(s), safe='') for s in [mod_id, version, *sub_path, file_name] if s]
    return _resolve_url('/depots/' + '/'.join(segments))


async def get_directory_contents(
    mod_id: str,
    version: Optional[str],
    sub_path: list[str] | None = None,
) -> Optional[list[dict]]:
    """List a directory inside a mod version (supports recursive sub-folder traversal).

    GET /depots/{id}/{version}/{...subPath}/
    Returns ``None`` if not found (404).
    """
    sub_path = sub_path or []
    segments = [quote(str(s), safe='') for s in [mod_id, version, *sub_path] if s]
    url = _resolve_url('/depots/' + '/'.join(segments) + '/')

    async with httpx.AsyncClient() as client:
        res = await client.get(url)

    if res.status_code == 404:
        return None
    if res.status_code != 200:
        raise RuntimeError(f'HTTP {res.status_code}')

    return parse_directory_listing(res.text)


async def get_storage_info() -> dict:
    """Get server storage info (free space and total size).

    GET /api/downloader/available-free-space
    """
    async with httpx.AsyncClient() as client:
        res = await client.get(_resolve_url('/api/downloader/available-free-space'))

    if res.status_code != 200:
        raise RuntimeError(f'HTTP {res.status_code}')

    return res.json()


def extract_mod_id(input_str: str) -> Optional[str]:
    """Extract a Steam Workshop mod ID from a URL or raw numeric string.

    Returns ``None`` if no ID can be found.
    """
    if not input_str or not isinstance(input_str, str):
        return None

    trimmed = input_str.strip()

    # Pure numeric ID
    if re.fullmatch(r'\d+', trimmed):
        return trimmed

    # Steam Workshop URL  (…?id=XXXXXXX…)
    try:
        parsed = urlparse(trimmed)
        params = parse_qs(parsed.query)
        id_values = params.get('id', [])
        if id_values and re.fullmatch(r'\d+', id_values[0]):
            return id_values[0]
    except Exception:
        pass

    # Fallback: first long numeric sequence (≥ 5 digits)
    match = re.search(r'(\d{5,})', trimmed)
    return match.group(1) if match else None

