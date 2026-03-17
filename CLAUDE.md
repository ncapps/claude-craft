# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This repo is a workspace for building Claude Code plugins and AI agents. Plugins extend Claude Code with custom skills, commands, agents, and hooks.

## Plugin Structure

Each plugin lives under `plugins/<plugin-name>/` and follows this layout:

```
plugins/<plugin-name>/
  .claude-plugin/
    plugin.json          # Plugin manifest (name, version, description, components)
  skills/
    <skill-name>/
      SKILL.md           # Skill prompt with YAML frontmatter
    references/          # Optional reference materials used by skills
  scripts/               # Optional helper scripts invoked by skills via ${CLAUDE_PLUGIN_ROOT}
```

### plugin.json manifest

Declares the plugin and lists its components. Example:

```json
{
  "name": "plugin-name",
  "version": "1.0.0",
  "description": "...",
  "author": "...",
  "skills": ["skills/skill-name"]
}
```

### SKILL.md format

Skills use YAML frontmatter for metadata, followed by a markdown system prompt:

```markdown
---
name: skill-name
description: >
  Trigger description — when Claude should invoke this skill.
  Include synonyms and user phrasings that should trigger it.
---

# Skill content (system prompt for Claude)
...
```

The `description` field controls when Claude automatically invokes the skill. It should be comprehensive — list trigger phrases, synonyms, and use cases so Claude reliably activates the skill.

## Active Plugins (`.claude/settings.json`)

The workspace has these official plugins enabled: `pyright-lsp`, `github`, `code-review`, `skill-creator`, `plugin-dev`, `ralph-loop`, `claude-md-management`.

Use the `plugin-dev` plugin skills for guided plugin creation, and `skill-creator` for creating and evaluating skills.
