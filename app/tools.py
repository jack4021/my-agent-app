"""Tools for the agent application.

This module provides LangChain tools for file operations, web search,
image search, news search, and website browsing capabilities.
"""

import re
import urllib.request
import urllib.parse
import asyncio

# noinspection PyPackageRequirements
import nest_asyncio
from datetime import datetime
from pathlib import Path
from langchain_core.tools import tool
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.tools.playwright.utils import create_async_playwright_browser
from ddgs import DDGS
from logging_config import logger

nest_asyncio.apply()

WORKING_DIR = Path("workspace")


def _ensure_workspace():
    """Ensure the workspace directory exists."""
    WORKING_DIR.mkdir(exist_ok=True)


def _resolve_path(path: str) -> Path:
    """Resolve a relative path within the workspace, ensuring it does not escape."""
    _ensure_workspace()
    return (WORKING_DIR / path).resolve()


@tool
def browse_website(url: str, timeout: int = 30) -> str:
    """Browse a website and extract all text content.

    Args:
        url: The URL of the website to browse.
        timeout: Maximum time to wait for the page to load (in seconds).

    Returns:
        The extracted text content or an error message.
    """
    logger.info(f"Tool: browse_website | url={url}")

    async def _browse():
        try:
            async_browser = create_async_playwright_browser()
            toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=async_browser)
            tools = toolkit.get_tools()
            tools_by_name = {tool.name: tool for tool in tools}

            navigate_browser = tools_by_name["navigate_browser"]
            extract_text = tools_by_name["extract_text"]

            await navigate_browser.arun(
                tool_input={"url": url, "timeout": timeout * 1000}
            )
            text = await extract_text.arun(tool_input={})

            await async_browser.close()
            return text if text else "No text content found on page."
        except Exception as e:
            return f"Error browsing website: {str(e)}"

    return asyncio.run(_browse())


@tool
def get_file_metadata(path: str) -> str:
    """Get metadata for a file or directory.

    Args:
        path: Relative path to the file or directory from the root.

    Returns:
        Formatted metadata including size, type, and timestamps.
    """
    logger.info(f"Tool: get_file_metadata | path={path}")
    _ensure_workspace()
    resolved = _resolve_path(path)

    if not resolved.exists():
        return f"Error: Path '{path}' does not exist"

    try:
        stat = resolved.stat()
        fmt = "%Y-%m-%d %H:%M:%S"
        lines = [
            f"Size: {stat.st_size} bytes",
            f"Is file: {resolved.is_file()}",
            f"Is directory: {resolved.is_dir()}",
            f"Created: {datetime.fromtimestamp(stat.st_ctime).strftime(fmt)}",
            f"Modified: {datetime.fromtimestamp(stat.st_mtime).strftime(fmt)}",
            f"Accessed: {datetime.fromtimestamp(stat.st_atime).strftime(fmt)}",
        ]
        return "\n".join(lines)
    except Exception as e:
        return f"Error getting metadata: {str(e)}"


@tool
def web_search(query: str, max_results: int = 5, safesearch: str = "off") -> str:
    """Search the web using DuckDuckGo.

    Args:
        query: Search keywords.
        max_results: Number of results to return (default 5).
        safesearch: Safe search setting (default "off").

    Returns:
        Formatted web search results with title, URL, and snippet.
    """
    logger.info(f"Tool: web_search | query={query} | max_results={max_results}")
    try:
        results = DDGS().text(query, max_results=max_results, safesearch=safesearch)
        if not results:
            return "No results found."

        lines = ["Web Search Results:", ""]
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. {r.get('title', 'N/A')}")
            lines.append(f"   URL: {r.get('href', 'N/A')}")
            lines.append(f"   {r.get('body', 'N/A')}")
            lines.append("")
        return "\n".join(lines)
    except Exception as e:
        return f"Search error: {str(e)}"


IMGS_DIR = WORKING_DIR / "imgs"


def _sanitize_filename(name: str) -> str:
    """Sanitize a filename by removing special characters and limiting length.

    Args:
        name: The original filename or title to sanitize.

    Returns:
        A sanitized string safe for use as a filename, limited to 100 characters.
    """
    name = re.sub(r"[^a-zA-Z0-9\s]", "_", name)
    name = name.strip()
    return name[:100] if len(name) > 100 else name


def _get_extension(url: str) -> str:
    """Extract the file extension from an image URL.

    Args:
        url: The URL of the image file.

    Returns:
        The lowercase file extension including the dot (e.g., '.jpg', '.png').
        Defaults to '.jpg' if no recognized extension is found.
    """
    parsed = urllib.parse.urlparse(url)
    path = parsed.path.lower()
    for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"]:
        if ext in path:
            return ext
    return ".jpg"


@tool
def image_search(
    query: str, max_results: int = 5, safesearch: str = "off", size: str | None = None
) -> str:
    """Search for images using DuckDuckGo and save them to the imgs folder. Default values
    should be used unless specifically requested.

    Args:
        query: Search keywords.
        max_results: Number of results to return (default 5).
        safesearch: Safe search setting (default "off").
        size: Image size. Can be small, medium, large, or wallpaper. (default None).

    Returns:
        Formatted image search results with titles and local file paths.
    """
    logger.info(f"Tool: image_search | query={query} | max_results={max_results}")
    IMGS_DIR.mkdir(parents=True, exist_ok=True)

    try:
        results = DDGS().images(
            query, max_results=max_results, safesearch=safesearch, size=size
        )
        if not results:
            return "No image results found."

        lines = ["Image Search Results:", ""]
        for i, r in enumerate(results, 1):
            title = r.get("title", f"image_{i}")
            image_url = r.get("image", "")
            source_url = r.get("url", "")

            filename = _sanitize_filename(title) + _get_extension(image_url)
            saved = False

            if image_url:
                try:
                    req = urllib.request.Request(
                        image_url, headers={"User-Agent": "Mozilla/5.0"}
                    )
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        (IMGS_DIR / filename).write_bytes(resp.read())
                    saved = True
                except Exception:
                    saved = False

            lines.append(f"{i}. {title}")
            if saved:
                lines.append(f"   Saved to: imgs/{filename}")
            else:
                lines.append(f"   Failed to download: {image_url}")
            if source_url:
                lines.append(f"   Source: {source_url}")
            lines.append("")

        return "\n".join(lines)
    except Exception as e:
        return f"Search error: {str(e)}"


@tool
def news_search(query: str, max_results: int = 5, safesearch: str = "off") -> str:
    """Search for news using DuckDuckGo.

    Args:
        query: Search keywords.
        max_results: Number of results to return (default 5).
        safesearch: Safe search setting (default "off").

    Returns:
        Formatted news results with title, source, date, and URL.
    """
    logger.info(f"Tool: news_search | query={query} | max_results={max_results}")
    try:
        results = DDGS().news(query, max_results=max_results, safesearch=safesearch)
        if not results:
            return "No news results found."

        lines = ["News Search Results:", ""]
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. {r.get('title', 'N/A')}")
            lines.append(f"   Source: {r.get('source', 'N/A')}")
            lines.append(f"   Date: {r.get('date', 'N/A')}")
            lines.append(f"   URL: {r.get('url', 'N/A')}")
            lines.append(f"   {r.get('body', 'N/A')}")
            lines.append("")
        return "\n".join(lines)
    except Exception as e:
        return f"Search error: {str(e)}"


def get_tools():
    """Return list of all available tools."""
    return [get_file_metadata, web_search, image_search, news_search, browse_website]
