"""
Web Loader.

Loads text content from web pages and converts it
into the project's standard Document format.
"""

from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from config.logging_config import logger
from models.document import Document


class WebLoader:
    """
    Loads and extracts readable text from web pages.
    """

    def __init__(
        self,
        timeout: int = 15,
    ) -> None:
        """
        Initialize the web loader.
        """

        self.timeout = timeout

    # ==================================================
    # URL VALIDATION
    # ==================================================

    def _validate_url(
        self,
        url: str,
    ) -> None:
        """
        Validate the supplied URL.
        """

        if not url or not url.strip():
            raise ValueError("URL cannot be empty.")

        parsed = urlparse(url.strip())

        if parsed.scheme not in {"http", "https"}:
            raise ValueError("URL must start with http:// or https://")

        if not parsed.netloc:
            raise ValueError("Invalid URL: missing domain.")

    # ==================================================
    # LOAD WEB PAGE
    # ==================================================

    def load(
        self,
        url: str,
    ) -> list[Document]:
        """
        Download a web page and extract readable text.

        Parameters
        ----------
        url : str
            Web page URL.

        Returns
        -------
        list[Document]
            Extracted web document.
        """

        url = url.strip()

        self._validate_url(url)

        logger.info(f"Loading web page: {url}")

        headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/131.0 Safari/537.36"
            )
        }

        try:

            response = requests.get(
                url,
                headers=headers,
                timeout=self.timeout,
            )

            response.raise_for_status()

        except requests.RequestException as exc:

            logger.exception(f"Failed to download web page: {exc}")

            raise RuntimeError(f"Unable to load web page: {url}") from exc

        # --------------------------------------------------
        # Parse HTML
        # --------------------------------------------------

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        # Remove elements that do not contain
        # useful article content.

        for element in soup(
            [
                "script",
                "style",
                "noscript",
                "nav",
                "footer",
                "header",
                "aside",
            ]
        ):
            element.decompose()

        # --------------------------------------------------
        # Extract title
        # --------------------------------------------------

        title = ""

        if soup.title:
            title = soup.title.get_text(
                " ",
                strip=True,
            )

        # --------------------------------------------------
        # Extract text
        # --------------------------------------------------

        text = soup.get_text(
            separator="\n",
            strip=True,
        )

        # Clean excessive blank lines

        lines = [line.strip() for line in text.splitlines() if line.strip()]

        extracted_text = "\n".join(lines)

        if not extracted_text:

            logger.warning(f"No readable text extracted from: {url}")

            return []

        logger.success(
            f"Successfully extracted "
            f"{len(extracted_text)} characters "
            f"from web page."
        )

        # --------------------------------------------------
        # Metadata
        # --------------------------------------------------

        metadata = {
            "source": url,
            "file_name": title or url,
            "extension": ".html",
            "content_type": "web",
            "extraction_method": "beautifulsoup",
            "title": title,
            "url": url,
        }

        document = Document(
            content=extracted_text,
            source=url,
            source_type="web",
            metadata=metadata,
        )

        return [document]
