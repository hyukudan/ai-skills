#!/usr/bin/env python3
"""
Update all skills to be compatible with AgentSkills spec.
Adds: license, allowed-tools, compatibility (where needed)
"""

import os
import re
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent / "examples" / "skills"

# Define allowed-tools by category pattern
ALLOWED_TOOLS_MAP = {
    # Marketing skills - analysis and research
    "marketing/": "Read WebFetch",
    "cro": "Read WebFetch",
    "copywriting": "Read WebFetch",
    "seo": "Read WebFetch",
    "email": "Read WebFetch",
    "social": "Read WebFetch",
    "pricing": "Read WebFetch",
    "launch": "Read WebFetch",
    "referral": "Read WebFetch",
    "ads": "Read WebFetch",
    "analytics": "Read WebFetch",

    # Development - code manipulation
    "development/api": "Read Edit Bash WebFetch",
    "development/architecture": "Read Edit Bash",
    "development/debugging": "Read Edit Bash Grep",
    "development/testing": "Read Edit Bash",
    "development/security": "Read Edit Bash Grep",
    "development/": "Read Edit Bash",

    # DevOps - infrastructure
    "devops/": "Read Edit Bash",
    "docker": "Read Edit Bash",
    "kubernetes": "Read Edit Bash",
    "ci-cd": "Read Edit Bash",
    "logging": "Read Edit Bash",
    "incident": "Read Edit Bash",

    # Data - scripts and queries
    "data/": "Read Edit Bash",
    "databases/": "Read Edit Bash",
    "sql": "Read Edit Bash",
    "pandas": "Read Edit Bash",
    "pipeline": "Read Edit Bash",
    "visualization": "Read Edit Bash",

    # AI/ML - APIs and code
    "ai/": "Read Edit Bash WebFetch",
    "rag": "Read Edit Bash WebFetch",
    "agent": "Read Edit Bash WebFetch",
    "vector": "Read Edit Bash WebFetch",
    "llm": "Read Edit Bash WebFetch",
    "ml": "Read Edit Bash WebFetch",
    "fine-tuning": "Read Edit Bash WebFetch",

    # Cloud - CLI and configs
    "cloud/": "Read Edit Bash",
    "aws": "Read Edit Bash",
    "serverless": "Read Edit Bash",
    "infrastructure": "Read Edit Bash",
    "terraform": "Read Edit Bash",
    "cost": "Read Edit Bash",

    # Product/UX - research focused
    "product/": "Read WebFetch WebSearch",
    "user-research": "Read WebFetch WebSearch",
    "product-metrics": "Read WebFetch",
    "ux-writing": "Read Edit",

    # Mobile - code and builds
    "mobile/": "Read Edit Bash",
    "react-native": "Read Edit Bash",

    # Frontend
    "frontend": "Read Edit Bash",
    "nextjs": "Read Edit Bash",
    "tailwind": "Read Edit",
    "react": "Read Edit Bash",
    "typescript": "Read Edit Bash",

    # Git
    "git": "Read Edit Bash",

    # Misc
    "documentation": "Read Edit",
    "refactoring": "Read Edit Bash",
    "performance": "Read Edit Bash",
    "caching": "Read Edit Bash",
    "error": "Read Edit Bash",
    "async": "Read Edit Bash",
    "auth": "Read Edit Bash",
    "websocket": "Read Edit Bash",
    "graphql": "Read Edit Bash WebFetch",
    "redis": "Read Edit Bash",
    "postgresql": "Read Edit Bash",
}

# Default if no match
DEFAULT_ALLOWED_TOOLS = "Read Edit"

def get_allowed_tools(skill_name: str, category: str) -> str:
    """Determine allowed-tools based on skill name and category."""
    # Check category first
    for pattern, tools in ALLOWED_TOOLS_MAP.items():
        if pattern in category.lower():
            return tools

    # Check skill name
    for pattern, tools in ALLOWED_TOOLS_MAP.items():
        if pattern in skill_name.lower():
            return tools

    return DEFAULT_ALLOWED_TOOLS


def update_skill_file(skill_path: Path) -> bool:
    """Update a single skill file with spec-compliant fields."""
    try:
        content = skill_path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        # Try with latin-1 for binary files
        try:
            content = skill_path.read_text(encoding='latin-1')
        except:
            print(f"  ERROR: Cannot read {skill_path}")
            return False

    # Check if it has frontmatter
    if not content.startswith('---'):
        print(f"  SKIP: No frontmatter in {skill_path}")
        return False

    # Split frontmatter and body
    parts = content.split('---', 2)
    if len(parts) < 3:
        print(f"  SKIP: Invalid frontmatter in {skill_path}")
        return False

    frontmatter = parts[1]
    body = parts[2]

    # Extract current fields
    name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
    category_match = re.search(r'^category:\s*(.+)$', frontmatter, re.MULTILINE)

    skill_name = name_match.group(1).strip() if name_match else skill_path.parent.name
    category = category_match.group(1).strip() if category_match else ""

    # Check if already has the fields
    has_license = 'license:' in frontmatter
    has_allowed_tools = 'allowed-tools:' in frontmatter

    if has_license and has_allowed_tools:
        print(f"  OK: {skill_name} already has spec fields")
        return False

    # Determine allowed-tools
    allowed_tools = get_allowed_tools(skill_name, category)

    # Build new fields to add after description
    new_fields = []
    if not has_license:
        new_fields.append("license: MIT")
    if not has_allowed_tools:
        new_fields.append(f"allowed-tools: {allowed_tools}")

    if not new_fields:
        return False

    # Find where to insert (after description block)
    # Look for the end of description (next field after description)
    lines = frontmatter.strip().split('\n')
    new_lines = []
    inserted = False
    in_description = False

    for i, line in enumerate(lines):
        new_lines.append(line)

        # Detect description field
        if line.startswith('description:'):
            in_description = True
            continue

        # If we were in description and hit a new field, insert our fields
        if in_description and line and not line.startswith(' ') and not line.startswith('\t') and ':' in line:
            in_description = False
            if not inserted:
                # Insert before this line
                new_lines = new_lines[:-1]  # Remove last line
                for field in new_fields:
                    new_lines.append(field)
                new_lines.append(line)  # Add back the line
                inserted = True

    # If description was last, append at end
    if not inserted:
        for field in new_fields:
            new_lines.append(field)

    # Rebuild content
    new_frontmatter = '\n'.join(new_lines)
    new_content = f"---\n{new_frontmatter}\n---{body}"

    # Write back
    skill_path.write_text(new_content, encoding='utf-8')
    print(f"  UPDATED: {skill_name} <- {', '.join(new_fields)}")
    return True


def main():
    print("Updating skills to AgentSkills spec compliance...\n")

    updated = 0
    skipped = 0
    errors = 0

    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue

        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue

        try:
            if update_skill_file(skill_file):
                updated += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  ERROR: {skill_dir.name}: {e}")
            errors += 1

    print(f"\n{'='*50}")
    print(f"Updated: {updated}")
    print(f"Skipped: {skipped}")
    print(f"Errors:  {errors}")


if __name__ == "__main__":
    main()
