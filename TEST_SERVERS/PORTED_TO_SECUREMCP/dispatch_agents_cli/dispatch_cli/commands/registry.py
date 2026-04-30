"""Registry management commands."""

import re
from pathlib import Path

import typer

from dispatch_cli.logger import get_logger

from ..registry import list_agents_from_registry

registry_app = typer.Typer(name="registry", help="Registry management")


@registry_app.command("list")
def list_registry():
    """List all agents in registry."""
    logger = get_logger()
    try:
        agents = list_agents_from_registry()
        if not agents:
            logger.info("Registry is empty.")
            return

        logger.info(f"\n[bold]Registry Contents ({len(agents)} agents):[/bold]")
        for agent in agents:
            logger.info(f"\n  [cyan]{agent.name}[/cyan]")
            logger.info(f"    Agent UID: {agent.uid}")
            logger.info(f"    Network URL: {agent.get_network_url()}")
            image_tag = re.sub(r"[^a-z0-9-]", "-", f"dispatchagents-{agent.name}")
            logger.info(f"    Image: {image_tag}")
            logger.info(f"    Topics: {', '.join(agent.topics)}")
            logger.info(f"    Status: {agent.status}")
            logger.info(f"    Created: {agent.created_at}")
            if agent.last_heartbeat:
                logger.info(f"    Last Heartbeat: {agent.last_heartbeat}")
            if agent.metadata:
                logger.info(f"    Metadata: {agent.metadata}")
    except Exception as e:
        logger.error(f"Failed to list registry: {e}")
        raise typer.Exit(1)


@registry_app.command("locate")
def locate_registry():
    """Show registry database location."""
    logger = get_logger()
    registry_path = Path.home() / ".dispatch_agents" / "default" / "registry.db"
    exists = "✓" if registry_path.exists() else "✗"
    logger.info(f"Registry location: {registry_path}")
    logger.info(f"Exists: {exists}")


@registry_app.command("clear")
def clear_registry():
    """Clear all agents from registry."""
    logger = get_logger()
    registry_path = Path.home() / ".dispatch_agents" / "default" / "registry.db"

    if not registry_path.exists():
        logger.info("No registry found.")
        return

    confirm = typer.confirm("Are you sure you want to clear the entire registry?")
    if not confirm:
        logger.info("Cancelled.")
        return

    try:
        registry_path.unlink()
        logger.success("Registry cleared.")
    except Exception as e:
        logger.error(f"Failed to clear registry: {e}")
        raise typer.Exit(1)
