---
name: epub-reader
description: >
  This skill should be used when the user asks to read, parse, extract, open,
  load, or import an epub file or ebook. Also triggered when the user wants to
  convert an epub to markdown, extract chapters from a book, summarize a book,
  analyze book content for plugin creation, or turn a book into a Claude Code
  plugin or skill.
---

# EPUB Reader — Extract and Use Book Content

Parse epub files into structured markdown chapters, then use the extracted
content to create a Claude Code plugin or produce a book summary.

---

## Workflow

### Step 1: Get the epub path

Ask the user for the path to their epub file. Accept absolute or relative paths.

### Step 2: Extract chapters

Run the extraction script:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/epub_extract.py "<epub-path>" --output-dir "<output-dir>"
```

Default output directory is `./extracted`. The script produces:
- `manifest.json` — book metadata and ordered chapter list with word counts
- `chapters/` — numbered markdown files, one per chapter

If the script reports a DRM error, inform the user that DRM-protected epubs
cannot be extracted.

### Step 3: Present overview

Read `manifest.json` and present the user with:
- Book title and author
- Total chapter count and word count
- Numbered chapter list with titles and word counts

### Step 4: Choose a path

Ask the user which path they want:

**Path A — Create a plugin from this book**
Invoke the `plugin-dev:create-plugin` skill to start guided plugin creation.
The extracted chapters serve as reference material — read them selectively as
needed during the plugin design process. You do not need to read every chapter
upfront; read chapters on-demand as the plugin design requires specific content.

**Path B — Summarize the book**
Read chapters selectively (prioritize longer chapters and those with substantive
titles). Produce a structured summary saved as a markdown file:

```markdown
# Book Summary: <Title>
**Author:** <Author>

## Overview
<2-3 paragraph synopsis of the book's main thesis and approach>

## Key Concepts
<Bulleted list of the book's most important ideas, principles, or frameworks>

## Chapter Summaries
### <Chapter Title>
<2-4 sentence summary of each chapter>
...

## Patterns & Methodologies
<Any named patterns, processes, or methodologies the book teaches>

## Potential Plugin Topics
<Suggest 2-3 plugin ideas based on the book's content>
```

Save the summary in the same directory as the extracted content.

---

## Important Notes

- The extraction script uses Python stdlib only — no pip install needed
- Claude's Read tool has a 256KB limit. The script splits content into per-chapter
  files to stay within this limit. If any single chapter exceeds the limit, read
  it in parts using the offset/limit parameters
- Consult `${CLAUDE_PLUGIN_ROOT}/skills/epub-reader/references/epub-format.md`
  for details on epub structure if troubleshooting extraction issues
- If the script fails with a non-DRM error, inspect the error message and
  consult the reference doc to determine if the epub is malformed or uses an
  unusual structure
- The script handles epub2 and epub3 formats, encoding fallbacks, and common
  publisher quirks
