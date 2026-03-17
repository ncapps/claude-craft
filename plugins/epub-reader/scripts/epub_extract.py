#!/usr/bin/env python3
"""Extract epub contents into markdown chapters with a manifest.

Usage:
    python3 epub_extract.py <epub-path> [--output-dir <dir>]

Output:
    <output-dir>/<book-slug>/
        manifest.json     # metadata + ordered chapter list
        chapters/
            01-chapter-title.md
            02-chapter-title.md
            ...

Dependencies: Python stdlib only.
"""

import argparse
import json
import os
import re
import zipfile
from html.parser import HTMLParser
from xml.etree import ElementTree as ET

# XML namespaces used in epub files
NS = {
    "container": "urn:oasis:names:tc:opendocument:xmlns:container",
    "opf": "http://www.idpf.org/2007/opf",
    "dc": "http://purl.org/dc/elements/1.1/",
    "xhtml": "http://www.w3.org/1999/xhtml",
    "ncx": "http://www.daisy.org/z3986/2005/ncx/",
    "epub": "http://www.idpf.org/2007/ops",
}


class HTMLToMarkdown(HTMLParser):
    """Convert HTML/XHTML to markdown, preserving structure."""

    def __init__(self):
        super().__init__()
        self.output = []
        self.current_line = []
        self._tag_stack = []
        self._list_stack = []  # stack of ('ul'|'ol', counter)
        self._in_pre = False
        self._in_code = False
        self._skip = False  # skip content inside <style>, <script>
        self._heading_level = 0

    def _flush_line(self):
        text = "".join(self.current_line)
        self.current_line = []
        if text.strip() or self._in_pre:
            self.output.append(text)

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        self._tag_stack.append(tag)

        if tag in ("style", "script"):
            self._skip = True
            return

        if self._skip:
            return

        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._flush_line()
            self._heading_level = int(tag[1])
            self.current_line.append("#" * self._heading_level + " ")

        elif tag == "p":
            self._flush_line()

        elif tag == "br":
            self._flush_line()

        elif tag == "pre":
            self._flush_line()
            self._in_pre = True
            if not self._in_code:
                self.output.append("```")

        elif tag == "code":
            if self._in_pre:
                # <pre><code> — already opened fence
                pass
            else:
                self._in_code = True
                if self._is_block_code(attrs):
                    self._flush_line()
                    self._in_pre = True
                    self.output.append("```")
                else:
                    self.current_line.append("`")

        elif tag in ("strong", "b"):
            self.current_line.append("**")

        elif tag in ("em", "i"):
            self.current_line.append("*")

        elif tag == "ul":
            self._flush_line()
            self._list_stack.append(("ul", 0))

        elif tag == "ol":
            self._flush_line()
            self._list_stack.append(("ol", 0))

        elif tag == "li":
            self._flush_line()
            indent = "  " * max(0, len(self._list_stack) - 1)
            if self._list_stack:
                kind, count = self._list_stack[-1]
                if kind == "ol":
                    count += 1
                    self._list_stack[-1] = (kind, count)
                    self.current_line.append(f"{indent}{count}. ")
                else:
                    self.current_line.append(f"{indent}- ")

        elif tag == "blockquote":
            self._flush_line()
            self.current_line.append("> ")

        elif tag == "hr":
            self._flush_line()
            self.output.append("---")

        elif tag == "img":
            alt = dict(attrs).get("alt", "")
            self.current_line.append(f"[{alt}]")

    def handle_endtag(self, tag):
        tag = tag.lower()

        if tag in ("style", "script"):
            self._skip = False
            if self._tag_stack and self._tag_stack[-1] == tag:
                self._tag_stack.pop()
            return

        if self._skip:
            return

        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._flush_line()
            self.output.append("")  # blank line after heading
            self._heading_level = 0

        elif tag == "p":
            self._flush_line()
            self.output.append("")

        elif tag == "pre":
            self._flush_line()
            self._in_pre = False
            if not self._in_code:
                self.output.append("```")
                self.output.append("")

        elif tag == "code":
            if self._in_pre:
                # closing <pre><code> — close fence
                self._flush_line()
                self._in_pre = False
                self._in_code = False
                self.output.append("```")
                self.output.append("")
            elif self._in_code and not self._in_pre:
                # was a block code without pre
                self._flush_line()
                self._in_pre = False
                self._in_code = False
                self.output.append("```")
                self.output.append("")
            else:
                self.current_line.append("`")

        elif tag in ("strong", "b"):
            self.current_line.append("**")

        elif tag in ("em", "i"):
            self.current_line.append("*")

        elif tag in ("ul", "ol"):
            self._flush_line()
            if self._list_stack:
                self._list_stack.pop()
            self.output.append("")

        elif tag == "li":
            self._flush_line()

        elif tag == "blockquote":
            self._flush_line()
            self.output.append("")

        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()

    def handle_data(self, data):
        if self._skip:
            return
        if self._in_pre:
            self.current_line.append(data)
        else:
            # Collapse whitespace
            text = re.sub(r"\s+", " ", data)
            if text.strip():
                self.current_line.append(text)

    def handle_entityref(self, name):
        entities = {
            "amp": "&", "lt": "<", "gt": ">", "quot": '"',
            "apos": "'", "nbsp": " ", "mdash": "—", "ndash": "–",
            "lsquo": "\u2018", "rsquo": "\u2019",
            "ldquo": "\u201c", "rdquo": "\u201d",
            "hellip": "\u2026",
        }
        self.current_line.append(entities.get(name, f"&{name};"))

    def handle_charref(self, name):
        try:
            if name.startswith("x"):
                char = chr(int(name[1:], 16))
            else:
                char = chr(int(name))
            self.current_line.append(char)
        except (ValueError, OverflowError):
            self.current_line.append(f"&#{name};")

    def _is_block_code(self, attrs):
        """Heuristic: treat <code> as block if it has a class suggesting language."""
        classes = dict(attrs).get("class", "")
        return bool(re.search(r"(language-|lang-|highlight|sourceCode)", classes))

    def get_markdown(self):
        self._flush_line()
        text = "\n".join(self.output)
        # Clean up excessive blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip() + "\n"


def html_to_markdown(html_content):
    """Convert HTML string to markdown."""
    parser = HTMLToMarkdown()
    parser.feed(html_content)
    return parser.get_markdown()


def slugify(text):
    """Convert text to a filename-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")[:60]


def word_count(text):
    """Count words in text."""
    return len(text.split())


def check_drm(zf):
    """Check if epub has DRM encryption."""
    try:
        encryption = zf.read("META-INF/encryption.xml").decode("utf-8")
        if "EncryptedData" in encryption:
            return True
    except KeyError:
        pass
    return False


def find_opf_path(zf):
    """Parse container.xml to find the OPF file path."""
    container_xml = zf.read("META-INF/container.xml").decode("utf-8")
    root = ET.fromstring(container_xml)
    rootfile = root.find(
        ".//container:rootfile[@media-type='application/oebps-package+xml']",
        NS,
    )
    if rootfile is None:
        # Try without namespace (some epubs are non-conformant)
        rootfile = root.find(".//{*}rootfile[@media-type='application/oebps-package+xml']")
    if rootfile is None:
        raise ValueError("Could not find OPF rootfile in container.xml")
    return rootfile.get("full-path")


def parse_opf(zf, opf_path):
    """Parse OPF file to extract metadata, manifest, and spine."""
    opf_dir = os.path.dirname(opf_path)
    opf_xml = zf.read(opf_path).decode("utf-8")
    root = ET.fromstring(opf_xml)

    # Metadata
    metadata = {}
    meta_el = root.find("opf:metadata", NS)
    if meta_el is None:
        meta_el = root.find("{*}metadata")

    if meta_el is not None:
        title_el = meta_el.find("dc:title", NS)
        if title_el is None:
            title_el = meta_el.find("{*}title")
        metadata["title"] = title_el.text.strip() if title_el is not None and title_el.text else "Unknown"

        creator_el = meta_el.find("dc:creator", NS)
        if creator_el is None:
            creator_el = meta_el.find("{*}creator")
        metadata["author"] = creator_el.text.strip() if creator_el is not None and creator_el.text else "Unknown"

        lang_el = meta_el.find("dc:language", NS)
        if lang_el is None:
            lang_el = meta_el.find("{*}language")
        metadata["language"] = lang_el.text.strip() if lang_el is not None and lang_el.text else "en"

    # Manifest — map id → href (resolved to ZIP path)
    manifest = {}
    manifest_el = root.find("opf:manifest", NS)
    if manifest_el is None:
        manifest_el = root.find("{*}manifest")

    if manifest_el is not None:
        for item in manifest_el:
            item_id = item.get("id")
            href = item.get("href")
            media_type = item.get("media-type", "")
            if item_id and href:
                # Resolve path relative to OPF directory
                full_path = os.path.normpath(os.path.join(opf_dir, href)) if opf_dir else href
                manifest[item_id] = {
                    "href": full_path,
                    "media_type": media_type,
                }

    # Spine — ordered list of manifest IDs
    spine = []
    spine_el = root.find("opf:spine", NS)
    if spine_el is None:
        spine_el = root.find("{*}spine")

    if spine_el is not None:
        for itemref in spine_el:
            idref = itemref.get("idref")
            if idref:
                spine.append(idref)

    # Try to get chapter titles from NCX or nav
    chapter_titles = {}
    toc_id = spine_el.get("toc") if spine_el is not None else None
    if toc_id and toc_id in manifest:
        ncx_path = manifest[toc_id]["href"]
        chapter_titles = parse_ncx(zf, ncx_path, opf_dir)

    if not chapter_titles:
        chapter_titles = parse_nav_xhtml(zf, manifest, opf_dir)

    return metadata, manifest, spine, chapter_titles


def parse_ncx(zf, ncx_path, opf_dir):
    """Parse toc.ncx for chapter titles mapped to content hrefs."""
    titles = {}
    try:
        ncx_xml = zf.read(ncx_path).decode("utf-8")
        root = ET.fromstring(ncx_xml)
        for nav_point in root.iter("{http://www.daisy.org/z3986/2005/ncx/}navPoint"):
            label_el = nav_point.find("{http://www.daisy.org/z3986/2005/ncx/}navLabel/{http://www.daisy.org/z3986/2005/ncx/}text")
            content_el = nav_point.find("{http://www.daisy.org/z3986/2005/ncx/}content")
            if label_el is not None and content_el is not None and label_el.text:
                src = content_el.get("src", "")
                # Remove fragment
                src = src.split("#")[0]
                # Resolve relative to NCX location
                ncx_dir = os.path.dirname(ncx_path)
                full_src = os.path.normpath(os.path.join(ncx_dir, src)) if ncx_dir else src
                titles[full_src] = label_el.text.strip()
    except (KeyError, ET.ParseError):
        pass
    return titles


def parse_nav_xhtml(zf, manifest, opf_dir):
    """Parse epub3 nav.xhtml for chapter titles."""
    titles = {}
    for item_id, item in manifest.items():
        if "nav" in item_id.lower() and item["media_type"] == "application/xhtml+xml":
            try:
                nav_html = zf.read(item["href"]).decode("utf-8")
                # Simple regex extraction of nav links
                for match in re.finditer(
                    r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
                    nav_html,
                    re.DOTALL,
                ):
                    href, label = match.groups()
                    href = href.split("#")[0]
                    label = re.sub(r"<[^>]+>", "", label).strip()
                    if href and label:
                        nav_dir = os.path.dirname(item["href"])
                        full_href = os.path.normpath(os.path.join(nav_dir, href)) if nav_dir else href
                        titles[full_href] = label
            except (KeyError, UnicodeDecodeError):
                pass
            break
    return titles


def read_zip_file(zf, path):
    """Read a file from the ZIP, trying UTF-8 then latin-1."""
    raw = zf.read(path)
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1")


def extract_title_from_html(html_content):
    """Extract title from first heading in HTML content."""
    match = re.search(r"<h[1-3][^>]*>(.*?)</h[1-3]>", html_content, re.DOTALL | re.IGNORECASE)
    if match:
        title = re.sub(r"<[^>]+>", "", match.group(1)).strip()
        if title:
            return title
    # Try <title> tag
    match = re.search(r"<title>(.*?)</title>", html_content, re.DOTALL | re.IGNORECASE)
    if match:
        title = match.group(1).strip()
        if title:
            return title
    return None


def extract_epub(epub_path, output_dir):
    """Extract an epub file into markdown chapters with a manifest."""
    if not os.path.exists(epub_path):
        print(f"Error: File not found: {epub_path}")
        return 1

    if not zipfile.is_zipfile(epub_path):
        print(f"Error: Not a valid ZIP/epub file: {epub_path}")
        return 1

    with zipfile.ZipFile(epub_path, "r") as zf:
        # Check for DRM
        if check_drm(zf):
            print("Error: This epub appears to be DRM-protected and cannot be extracted.")
            return 1

        # Find and parse OPF
        opf_path = find_opf_path(zf)
        metadata, manifest, spine, chapter_titles = parse_opf(zf, opf_path)

        book_slug = slugify(metadata.get("title", "unknown-book"))
        book_dir = os.path.join(output_dir, book_slug)
        chapters_dir = os.path.join(book_dir, "chapters")
        os.makedirs(chapters_dir, exist_ok=True)

        print(f"Extracting: {metadata.get('title', 'Unknown')}")
        print(f"Author: {metadata.get('author', 'Unknown')}")
        print(f"Output: {book_dir}")

        # Process spine items
        chapter_index = []
        chapter_num = 0

        for spine_id in spine:
            if spine_id not in manifest:
                continue

            item = manifest[spine_id]
            if item["media_type"] not in (
                "application/xhtml+xml",
                "text/html",
                "application/xml",
            ):
                continue

            try:
                html_content = read_zip_file(zf, item["href"])
            except KeyError:
                print(f"  Warning: Could not read {item['href']}, skipping")
                continue

            # Convert to markdown
            md_content = html_to_markdown(html_content)

            # Skip nearly empty chapters (nav pages, cover pages with no text)
            if word_count(md_content) < 5:
                continue

            chapter_num += 1

            # Determine chapter title
            title = chapter_titles.get(item["href"])
            if not title:
                title = extract_title_from_html(html_content)
            if not title:
                title = f"Chapter {chapter_num}"

            # Write chapter file
            filename = f"{chapter_num:02d}-{slugify(title)}.md"
            filepath = os.path.join(chapters_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(md_content)

            wc = word_count(md_content)
            chapter_index.append({
                "number": chapter_num,
                "title": title,
                "filename": filename,
                "word_count": wc,
            })
            print(f"  [{chapter_num:02d}] {title} ({wc:,} words)")

        # Write manifest
        total_words = sum(ch["word_count"] for ch in chapter_index)
        manifest_data = {
            "title": metadata.get("title", "Unknown"),
            "author": metadata.get("author", "Unknown"),
            "language": metadata.get("language", "en"),
            "source_file": os.path.basename(epub_path),
            "total_chapters": len(chapter_index),
            "total_words": total_words,
            "chapters": chapter_index,
        }

        manifest_path = os.path.join(book_dir, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)

        print(f"\nDone: {len(chapter_index)} chapters, {total_words:,} words total")
        print(f"Manifest: {manifest_path}")
        return 0


def main():
    parser = argparse.ArgumentParser(
        description="Extract epub contents into markdown chapters"
    )
    parser.add_argument("epub_path", help="Path to the epub file")
    parser.add_argument(
        "--output-dir",
        default="./extracted",
        help="Output directory (default: ./extracted)",
    )
    args = parser.parse_args()
    return extract_epub(args.epub_path, args.output_dir)


if __name__ == "__main__":
    raise SystemExit(main())
