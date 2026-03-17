# claude-craft

A workspace for building Claude Code plugins and AI agents.

## What's here

Plugins live under `plugins/<plugin-name>/` and extend Claude Code with custom skills, commands, agents, and hooks.

### Plugins

| Plugin | Description |
|--------|-------------|
| [epub-reader](plugins/epub-reader/) | Parses epub files into markdown chapters; guides you to create a plugin from the content or produce a structured summary |
| [oop-designer](plugins/oop-designer/) | Guides disciplined OOP design: requirements gathering, class design, design patterns, and Mermaid UML output |

## Plugin structure

```
plugins/<plugin-name>/
  .claude-plugin/
    plugin.json          # Manifest: name, version, description, components
  skills/
    <skill-name>/
      SKILL.md           # Skill prompt with YAML frontmatter
      references/        # Optional reference materials
  scripts/               # Optional helper scripts (invoked via ${CLAUDE_PLUGIN_ROOT})
```

## Building plugins

Use the `plugin-dev` skill suite for guided creation:

- `/plugin-dev:create-plugin` — end-to-end plugin creation workflow
- `/plugin-dev:skill-development` — create and refine skills
- `/plugin-dev:plugin-structure` — plugin layout and manifest guidance

Use `skill-creator` to evaluate and optimize skill trigger descriptions.

See [CLAUDE.md](CLAUDE.md) for full authoring guidance.
