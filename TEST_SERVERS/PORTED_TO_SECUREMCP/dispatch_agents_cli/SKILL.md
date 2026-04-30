# SKILL.md File Format Specification

A SKILL.md file defines a reusable skill for AI agents. Skills are designed for use with the [Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/skills) and other frameworks that support the SKILL.md format. They allow teams to share domain expertise, best practices, and standardized behaviors through the Skills Hub.

## File Structure

A SKILL.md file is a Markdown file with YAML frontmatter:

```markdown
---
name: my-skill-name
description: A short description of what this skill does.
---

# Skill Title

Instructions for the AI agent go here in Markdown.
```

## Frontmatter Fields

The YAML frontmatter block is delimited by `---` and contains metadata about the skill.

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Display name for the skill (max 128 characters) |
| `description` | Yes | What the skill does (max 1024 characters) |

## Skill ID

Each skill has a unique identifier (`skill_id`) that is separate from the display `name`:

- Must be **kebab-case**: lowercase letters, numbers, and hyphens only
- Cannot start or end with a hyphen
- Maximum 64 characters
- Pattern: `^[a-z0-9]+(?:-[a-z0-9]+)*$`
- If not provided during creation, auto-generated from the display name

Examples of valid skill IDs: `code-review`, `python-linter`, `deploy-helper`, `k8s-debug`

## Content Body

The Markdown body after the frontmatter contains the instructions for the AI agent. This is free-form Markdown and can include:

- Step-by-step instructions
- Code examples and templates
- Decision trees and conditional logic
- Tool usage patterns
- Best practices and constraints

### Content Constraints

- Maximum size: **100 KB** (100,000 characters)
- Cannot be empty or whitespace-only

## Installation Path

When installed via the CLI, skills are placed at:

```
.claude/skills/{skill_id}/SKILL.md
```

For example, installing a skill with ID `code-review` creates:

```
.claude/skills/code-review/SKILL.md
```

A custom installation path can be specified with the `--path` flag on `dispatch skills install`.

## Example

Below is a complete example of a SKILL.md file:

```markdown
---
name: Code Review Helper
description: Guides AI agents through structured code reviews with checklist-based evaluation.
---

# Code Review Helper

You are performing a structured code review. Follow this checklist for every review.

## Review Checklist

1. **Correctness**: Does the code do what it claims?
2. **Security**: Are there injection risks, hardcoded secrets, or unsafe patterns?
3. **Performance**: Are there unnecessary allocations, N+1 queries, or missing indexes?
4. **Readability**: Is the code clear and well-named?
5. **Tests**: Are edge cases covered?

## Output Format

Provide feedback as a numbered list matching the checklist above. For each item, state
either "Pass" or describe the issue with a suggested fix.
```

## CLI Commands

Use the Dispatch CLI to manage skills:

```bash
# Search for skills
dispatch skills search "code review"

# View skill details
dispatch skills show code-review

# Install a skill
dispatch skills install code-review

# Create a new skill
dispatch skills create "Code Review Helper" ./SKILL.md

# Update a skill you own
dispatch skills update code-review ./SKILL.md --name "Updated Name"

# Delete a skill you own
dispatch skills delete code-review
```

See the [CLI README](README.md#skills-hub) for full command options and flags.
