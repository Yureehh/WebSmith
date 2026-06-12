import re
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import httpx

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?:\+39\s?)?(?:0\d{1,3}[\s.-]?\d{5,8}|3\d{2}[\s.-]?\d{6,7})")
SOCIAL_HOSTS = ("linkedin.com", "instagram.com", "facebook.com", "tiktok.com")
INTERESTING_PAGE_TOKENS = (
    "about",
    "chi-siamo",
    "chisiamo",
    "servizi",
    "services",
    "contact",
    "contatti",
    "menu",
    "gallery",
    "galleria",
    "portfolio",
    "progetti",
    "projects",
)


class LinkTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.links: list[tuple[str, str]] = []
        self._in_title = False
        self._current_href: str | None = None
        self._current_text: list[str] = []
        self.text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag == "title":
            self._in_title = True
        if tag == "a" and attrs_dict.get("href"):
            self._current_href = attrs_dict["href"]
            self._current_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag == "a" and self._current_href:
            self.links.append((self._current_href, " ".join(self._current_text).strip()))
            self._current_href = None
            self._current_text = []

    def handle_data(self, data: str) -> None:
        clean = " ".join(data.split())
        if not clean:
            return
        if self._in_title:
            self.title += clean
        if self._current_href:
            self._current_text.append(clean)
        self.text_parts.append(clean)

    @property
    def text(self) -> str:
        return " ".join(self.text_parts)[:12000]


def normalize_url(url: str | None) -> str | None:
    if not url:
        return None
    if url.startswith(("http://", "https://")):
        return url
    return f"https://{url}"


def parse_html(html: str, source_url: str) -> dict:
    parser = LinkTextParser()
    parser.feed(html)
    base_host = urlparse(source_url).netloc
    interesting_pages = []
    socials = []
    for href, label in parser.links:
        full_url = urljoin(source_url, href)
        host = urlparse(full_url).netloc
        lower = f"{full_url} {label}".lower()
        if any(social in host for social in SOCIAL_HOSTS):
            socials.append(full_url)
        if host == base_host and any(token in lower for token in INTERESTING_PAGE_TOKENS):
            interesting_pages.append(full_url)
    return {
        "source_url": source_url,
        "title": parser.title or base_host,
        "content_text": parser.text,
        "extracted": {
            "emails": sorted(set(EMAIL_RE.findall(html))),
            "phones": sorted(set(PHONE_RE.findall(parser.text))),
            "socials": sorted(set(socials))[:10],
            "pages": sorted(set(interesting_pages))[:10],
        },
        "confidence": "medium",
    }


def fetch_public_site(url: str | None) -> dict:
    normalized = normalize_url(url)
    if not normalized:
        return {
            "source_url": "local://no-website",
            "title": "No website available",
            "content_text": "No website URL is known for this business yet.",
            "extracted": {"emails": [], "phones": [], "socials": [], "pages": []},
            "sources": [],
            "confidence": "low",
        }

    sources = []
    try:
        with httpx.Client(
            timeout=12,
            follow_redirects=True,
            headers={"User-Agent": "WebSmith/0.1 local enrichment"},
        ) as client:
            response = client.get(normalized)
            response.raise_for_status()
            html = response.text
            homepage = parse_html(html, str(response.url))
            sources.append(homepage)
            for page_url in homepage["extracted"]["pages"][:5]:
                try:
                    page_response = client.get(page_url)
                    page_response.raise_for_status()
                    sources.append(parse_html(page_response.text, str(page_response.url)))
                except Exception:
                    continue
    except Exception as exc:
        return {
            "source_url": normalized,
            "title": "Website fetch failed",
            "content_text": f"Could not fetch website: {exc}",
            "extracted": {"emails": [], "phones": [], "socials": [], "pages": []},
            "sources": [],
            "confidence": "low",
        }

    emails = sorted({email for source in sources for email in source["extracted"]["emails"]})
    phones = sorted({phone for source in sources for phone in source["extracted"]["phones"]})
    socials = sorted({social for source in sources for social in source["extracted"]["socials"]})
    pages = sorted({page for source in sources for page in source["extracted"]["pages"]})
    return {
        "source_url": sources[0]["source_url"],
        "title": sources[0]["title"],
        "content_text": "\n\n".join(source["content_text"] for source in sources)[:20000],
        "extracted": {
            "emails": emails,
            "phones": phones,
            "socials": socials[:10],
            "pages": pages[:10],
            "source_count": len(sources),
        },
        "sources": sources,
        "confidence": "medium",
    }
