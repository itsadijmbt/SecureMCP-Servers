"""Skills management commands."""

import re
from pathlib import Path
from typing import Annotated

import requests
import typer
from rich.table import Table

from dispatch_cli.auth import get_auth_headers, handle_auth_error
from dispatch_cli.logger import get_logger
from dispatch_cli.utils import DISPATCH_API_BASE

from .secrets import _NAMESPACE_SOURCE_DISPLAY, get_namespace_from_config

skills_app = typer.Typer(
    name="skills",
    help="Manage skills in the Skills Hub",
    rich_markup_mode="markdown",
)


def build_skills_url(endpoint: str, namespace: str) -> str:
    return f"{DISPATCH_API_BASE}/api/unstable/namespace/{namespace}/skills{endpoint}"


@skills_app.command("search")
def search_skills(
    query: Annotated[str | None, typer.Argument(help="Search query")] = None,
    namespace: Annotated[
        str | None,
        typer.Option(
            help="Namespace to search in (defaults to dispatch.yaml config)",
            envvar="DISPATCH_NAMESPACE",
        ),
    ] = None,
    limit: Annotated[int, typer.Option(help="Maximum number of results")] = 12,
):
    """Search for skills in the Skills Hub."""
    logger = get_logger()
    namespace, namespace_source = get_namespace_from_config(namespace, verify=True)

    # Show namespace information
    logger.info(
        f"Using namespace: [bold]{namespace}[/bold] [dim](from {_NAMESPACE_SOURCE_DISPLAY[namespace_source]})[/dim]"
    )

    # Get the current bearer credential for authentication
    auth_headers = get_auth_headers()

    try:
        params: dict[str, str | int] = {"limit": limit}
        if query:
            params["search"] = query

        with logger.status_context("Searching skills..."):
            response = requests.get(
                build_skills_url("", namespace),
                params=params,
                headers=auth_headers,
                timeout=30,
            )
            response.raise_for_status()

        result = response.json()
        skills = result.get("skills", [])
        total = result.get("total", 0)

        if not skills:
            if query:
                logger.info(f"No skills found matching '{query}'")
            else:
                logger.info("No skills found in this namespace")
            logger.info("\nTo create a skill, run:")
            logger.code(
                "dispatch skills create <name> <path-to-skill.md>", language="bash"
            )
            return

        # Display results as a table
        table = Table(title=f"Skills ({len(skills)} of {total})")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="bold")
        table.add_column("Author")
        table.add_column("Version")
        table.add_column("Description")

        for skill in skills:
            # Truncate description if too long
            desc = skill.get("description", "")
            if len(desc) > 50:
                desc = desc[:47] + "..."

            table.add_row(
                skill.get("skill_id", ""),
                skill.get("name", ""),
                skill.get("author", ""),
                str(skill.get("version", "")),
                desc,
            )

        logger.console.print(table)

        if total > len(skills):
            logger.info(
                f"\nShowing {len(skills)} of {total} results. Use --limit to see more."
            )

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            handle_auth_error("Invalid or expired API key")
        else:
            logger.error(f"HTTP Error: {e}")
            raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Failed to search skills: {e}")
        raise typer.Exit(1)


@skills_app.command("show")
def show_skill(
    skill_id: Annotated[str, typer.Argument(help="Skill ID to show")],
    namespace: Annotated[
        str | None,
        typer.Option(
            help="Namespace (defaults to dispatch.yaml config)",
            envvar="DISPATCH_NAMESPACE",
        ),
    ] = None,
):
    """Show details of a specific skill."""
    logger = get_logger()
    namespace, namespace_source = get_namespace_from_config(namespace, verify=True)

    logger.info(
        f"Using namespace: [bold]{namespace}[/bold] [dim](from {_NAMESPACE_SOURCE_DISPLAY[namespace_source]})[/dim]"
    )

    auth_headers = get_auth_headers()

    try:
        with logger.status_context(f"Fetching skill '{skill_id}'..."):
            response = requests.get(
                build_skills_url(f"/{skill_id}", namespace),
                headers=auth_headers,
                timeout=30,
            )
            response.raise_for_status()

        skill = response.json()

        # Display skill details
        logger.section(f"Skill: {skill.get('name', skill_id)}")
        logger.info(f"  [bold]ID:[/bold] {skill.get('skill_id', '')}")
        logger.info(f"  [bold]Author:[/bold] {skill.get('author', '')}")
        logger.info(f"  [bold]Version:[/bold] {skill.get('version', '')}")
        logger.info(f"  [bold]Created:[/bold] {skill.get('created_at', '')}")
        logger.info(f"  [bold]Updated:[/bold] {skill.get('updated_at', '')}")
        logger.info(f"  [bold]Description:[/bold] {skill.get('description', '')}")

        # Show content preview
        content = skill.get("content", "")
        if content:
            # Show first 20 lines
            lines = content.split("\n")
            preview = "\n".join(lines[:20])
            if len(lines) > 20:
                preview += f"\n... ({len(lines) - 20} more lines)"

            logger.info("\n[bold]Content Preview:[/bold]")
            logger.code(preview, language="markdown")

        logger.info("\n[bold]Commands:[/bold]")
        logger.code(
            f"dispatch skills install {skill_id} --namespace {namespace}",
            language="bash",
            title="To install this skill:",
        )

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            logger.error(f"Skill '{skill_id}' not found in namespace '{namespace}'")
        elif e.response.status_code == 401:
            handle_auth_error("Invalid or expired credential")
        else:
            logger.error(f"HTTP Error: {e}")
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Failed to get skill: {e}")
        raise typer.Exit(1)


@skills_app.command("install")
def install_skill(
    skill_id: Annotated[str, typer.Argument(help="Skill ID to install")],
    namespace: Annotated[
        str | None,
        typer.Option(
            help="Namespace (defaults to dispatch.yaml config)",
            envvar="DISPATCH_NAMESPACE",
        ),
    ] = None,
    path: Annotated[
        str | None,
        typer.Option(
            help="Custom installation path (default: .claude/skills/{skill_id}/SKILL.md)"
        ),
    ] = None,
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Overwrite existing file without prompting"),
    ] = False,
):
    """Install a skill from the Skills Hub to your local project."""
    logger = get_logger()
    namespace, namespace_source = get_namespace_from_config(namespace, verify=True)

    logger.info(
        f"Using namespace: [bold]{namespace}[/bold] [dim](from {_NAMESPACE_SOURCE_DISPLAY[namespace_source]})[/dim]"
    )

    # Determine installation path
    if path:
        install_path = Path(path)
    else:
        install_path = Path(".claude") / "skills" / skill_id / "SKILL.md"

    # Check if file exists
    if install_path.exists() and not force:
        logger.warning(f"File already exists: {install_path}")
        if not typer.confirm("Overwrite?"):
            logger.info("Installation cancelled")
            raise typer.Exit(0)

    auth_headers = get_auth_headers()

    try:
        with logger.status_context(f"Downloading skill '{skill_id}'..."):
            response = requests.get(
                build_skills_url(f"/{skill_id}/content", namespace),
                headers=auth_headers,
                timeout=30,
            )
            response.raise_for_status()

        content = response.text

        # Create parent directories
        install_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the file
        install_path.write_text(content)

        logger.success(f"Skill installed to: {install_path}")
        logger.info("\nThis skill is now available for Claude to use.")

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            logger.error(f"Skill '{skill_id}' not found in namespace '{namespace}'")
        elif e.response.status_code == 401:
            handle_auth_error("Invalid or expired credential")
        else:
            logger.error(f"HTTP Error: {e}")
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Failed to install skill: {e}")
        raise typer.Exit(1)


@skills_app.command("create")
def create_skill(
    name: Annotated[str, typer.Argument(help="Display name for the skill")],
    content_path: Annotated[
        str,
        typer.Argument(help="Path to SKILL.md file or directory containing SKILL.md"),
    ],
    namespace: Annotated[
        str | None,
        typer.Option(
            help="Namespace (defaults to dispatch.yaml config)",
            envvar="DISPATCH_NAMESPACE",
        ),
    ] = None,
    skill_id: Annotated[
        str | None,
        typer.Option(
            help="Skill ID (kebab-case, auto-generated from name if not provided)"
        ),
    ] = None,
    description: Annotated[
        str | None,
        typer.Option(help="Description of what the skill does"),
    ] = None,
    global_scope: Annotated[
        bool,
        typer.Option("--global", help="Share this skill to all namespaces in the org"),
    ] = False,
):
    """Create and upload a new skill to the Skills Hub."""
    logger = get_logger()
    namespace, namespace_source = get_namespace_from_config(namespace, verify=True)

    logger.info(
        f"Using namespace: [bold]{namespace}[/bold] [dim](from {_NAMESPACE_SOURCE_DISPLAY[namespace_source]})[/dim]"
    )

    # Resolve content path
    content_file = Path(content_path)
    if content_file.is_dir():
        content_file = content_file / "SKILL.md"

    if not content_file.exists():
        logger.error(f"File not found: {content_file}")
        raise typer.Exit(1)

    # Read content
    try:
        content = content_file.read_text()
    except Exception as e:
        logger.error(f"Failed to read file: {e}")
        raise typer.Exit(1)

    # Generate skill_id from name if not provided
    if not skill_id:
        # Convert to kebab-case: "My Cool Skill" -> "my-cool-skill"
        skill_id = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        logger.info(f"Generated skill ID: {skill_id}")

    # Prompt for description if not provided
    if not description:
        description = typer.prompt(
            "Enter a description for this skill",
            default="",
        )

    auth_headers = get_auth_headers()

    try:
        with logger.status_context(f"Creating skill '{skill_id}'..."):
            response = requests.post(
                build_skills_url("", namespace),
                json={
                    "skill_id": skill_id,
                    "name": name,
                    "description": description,
                    "content": content,
                    "org_scoped": global_scope,
                },
                headers=auth_headers,
                timeout=30,
            )
            response.raise_for_status()

        result = response.json()
        logger.success(f"Skill '{result.get('name', skill_id)}' created successfully!")
        logger.info(f"  ID: {result.get('skill_id', '')}")
        logger.info(f"  Version: {result.get('version', 1)}")

        logger.info("\nOthers can install this skill with:")
        logger.code(
            f"dispatch skills install {skill_id} --namespace {namespace}",
            language="bash",
        )

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 409:
            logger.error(
                f"Skill '{skill_id}' already exists in namespace '{namespace}'"
            )
            logger.info("Use 'dispatch skills update' to update an existing skill.")
        elif e.response.status_code == 401:
            handle_auth_error("Invalid or expired credential")
        elif e.response.status_code == 400:
            try:
                error_detail = e.response.json().get("detail", str(e))
                logger.error(f"Invalid request: {error_detail}")
            except Exception:
                logger.error(f"Invalid request: {e}")
        else:
            logger.error(f"HTTP Error: {e}")
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Failed to create skill: {e}")
        raise typer.Exit(1)


@skills_app.command("update")
def update_skill(
    skill_id: Annotated[str, typer.Argument(help="Skill ID to update")],
    content_path: Annotated[
        str | None, typer.Argument(help="Path to new SKILL.md file")
    ] = None,
    namespace: Annotated[
        str | None,
        typer.Option(
            help="Namespace (defaults to dispatch.yaml config)",
            envvar="DISPATCH_NAMESPACE",
        ),
    ] = None,
    name: Annotated[str | None, typer.Option(help="New display name")] = None,
    description: Annotated[str | None, typer.Option(help="New description")] = None,
):
    """Update an existing skill. You must be the owner to update."""
    logger = get_logger()
    namespace, namespace_source = get_namespace_from_config(namespace, verify=True)

    logger.info(
        f"Using namespace: [bold]{namespace}[/bold] [dim](from {_NAMESPACE_SOURCE_DISPLAY[namespace_source]})[/dim]"
    )

    # Build update payload
    update_data: dict = {}

    if name:
        update_data["name"] = name

    if description is not None:
        update_data["description"] = description

    if content_path:
        content_file = Path(content_path)
        if content_file.is_dir():
            content_file = content_file / "SKILL.md"

        if not content_file.exists():
            logger.error(f"File not found: {content_file}")
            raise typer.Exit(1)

        try:
            update_data["content"] = content_file.read_text()
        except Exception as e:
            logger.error(f"Failed to read file: {e}")
            raise typer.Exit(1)

    if not update_data:
        logger.error(
            "At least one of --name, --description, or content_path must be provided"
        )
        raise typer.Exit(1)

    auth_headers = get_auth_headers()

    try:
        with logger.status_context(f"Updating skill '{skill_id}'..."):
            response = requests.put(
                build_skills_url(f"/{skill_id}", namespace),
                json=update_data,
                headers=auth_headers,
                timeout=30,
            )
            response.raise_for_status()

        result = response.json()
        logger.success(f"Skill '{result.get('name', skill_id)}' updated successfully!")
        logger.info(f"  Version: {result.get('version', '')}")

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            logger.error(f"Skill '{skill_id}' not found in namespace '{namespace}'")
        elif e.response.status_code == 403:
            logger.error("Permission denied: you are not the owner of this skill")
        elif e.response.status_code == 401:
            handle_auth_error("Invalid or expired credential")
        else:
            logger.error(f"HTTP Error: {e}")
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Failed to update skill: {e}")
        raise typer.Exit(1)


@skills_app.command("delete")
def delete_skill(
    skill_id: Annotated[str, typer.Argument(help="Skill ID to delete")],
    namespace: Annotated[
        str | None,
        typer.Option(
            help="Namespace (defaults to dispatch.yaml config)",
            envvar="DISPATCH_NAMESPACE",
        ),
    ] = None,
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Delete without confirmation"),
    ] = False,
):
    """Delete a skill from the Skills Hub. You must be the owner to delete."""
    logger = get_logger()
    namespace, namespace_source = get_namespace_from_config(namespace, verify=True)

    logger.info(
        f"Using namespace: [bold]{namespace}[/bold] [dim](from {_NAMESPACE_SOURCE_DISPLAY[namespace_source]})[/dim]"
    )

    if not force:
        if not typer.confirm(f"Are you sure you want to delete skill '{skill_id}'?"):
            logger.info("Deletion cancelled")
            raise typer.Exit(0)

    auth_headers = get_auth_headers()

    try:
        with logger.status_context(f"Deleting skill '{skill_id}'..."):
            response = requests.delete(
                build_skills_url(f"/{skill_id}", namespace),
                headers=auth_headers,
                timeout=30,
            )
            response.raise_for_status()

        logger.success(f"Skill '{skill_id}' deleted successfully")

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            logger.error(f"Skill '{skill_id}' not found in namespace '{namespace}'")
        elif e.response.status_code == 403:
            logger.error("Permission denied: you are not the owner of this skill")
        elif e.response.status_code == 401:
            handle_auth_error("Invalid or expired credential")
        else:
            logger.error(f"HTTP Error: {e}")
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Failed to delete skill: {e}")
        raise typer.Exit(1)
