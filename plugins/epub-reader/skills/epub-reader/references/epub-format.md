# EPUB Format Reference

## Overview

EPUB is a ZIP-based ebook format. Every `.epub` file is a standard ZIP archive
containing XHTML content, metadata, and navigation files.

## ZIP Structure

```
META-INF/
  container.xml          # Entry point — declares where the OPF file lives
OEBPS/ (or content/)     # Content directory (name varies)
  content.opf            # Package document — metadata + manifest + spine
  toc.ncx                # Navigation (epub2) or nav.xhtml (epub3)
  chapter1.xhtml         # Content documents
  chapter2.xhtml
  images/
    cover.jpg
  styles/
    style.css
mimetype                 # Must be first file, contains "application/epub+zip"
```

## Key Files

### `META-INF/container.xml`

Always at this exact path. Declares the OPF location:

```xml
<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf"
              media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
```

### OPF Package Document (`content.opf`)

Three critical sections:

1. **`<metadata>`** — Title, author, language, identifiers
2. **`<manifest>`** — Lists every file in the epub with `id`, `href`, `media-type`
3. **`<spine>`** — Reading order as a sequence of `<itemref idref="..."/>` referencing manifest IDs

```xml
<package xmlns="http://www.idpf.org/2007/opf">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>Book Title</dc:title>
    <dc:creator>Author Name</dc:creator>
  </metadata>
  <manifest>
    <item id="ch1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
    <item id="ch2" href="chapter2.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="ch1"/>
    <itemref idref="ch2"/>
  </spine>
</package>
```

### Navigation

- **epub2:** `toc.ncx` file with `<navPoint>` elements containing labels and content references
- **epub3:** `nav.xhtml` file with an HTML `<nav epub:type="toc">` element containing an ordered list

## Common Quirks

### Content Paths
- Paths in the OPF manifest are relative to the OPF file's directory, not the ZIP root
- Some epubs use `OEBPS/`, others use `content/`, `OPS/`, or the ZIP root directly

### Namespaces
- OPF uses namespace `http://www.idpf.org/2007/opf`
- Dublin Core metadata uses `http://purl.org/dc/elements/1.1/`
- Container XML uses `urn:oasis:names:tc:opendocument:xmlns:container`
- XHTML content uses `http://www.w3.org/1999/xhtml`
- epub3 nav uses `http://www.idpf.org/2007/ops`

### Encoding
- Content files are typically UTF-8 but may declare other encodings
- Always try UTF-8 first, fall back to latin-1

### DRM
- DRM-protected epubs contain an `encryption.xml` in `META-INF/`
- These cannot be parsed — detect and fail gracefully

### epub2 vs epub3
- epub2: uses `toc.ncx` for navigation, `<guide>` element in OPF
- epub3: uses `nav.xhtml` with `epub:type="toc"`, `<metadata>` has `dcterms:modified`
- Many epubs are hybrid, containing both navigation formats

### Content Formatting
- Chapter content is XHTML — must handle self-closing tags (`<br/>`, `<img/>`)
- Code blocks may use `<pre>`, `<code>`, or `<pre><code>` wrapping
- Lists may be deeply nested
- Some publishers use `<div>` heavily instead of semantic HTML
- Inline styles are common — ignore for text extraction
