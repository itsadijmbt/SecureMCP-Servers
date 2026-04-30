"""Custom logger for Dispatch CLI using Rich for beautiful output.

Provides:
- Verbosity control (debug messages hidden by default)
- Rich formatting with colors and panels
- Status line updates (non-verbose mode) or full logs (verbose mode)
- Syntax-highlighted code blocks
"""

import sys
from contextlib import contextmanager
from io import StringIO
from typing import Literal

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.spinner import Spinner
from rich.table import Table

LogLevel = Literal["debug", "info", "success", "warning", "error"]


class DispatchLogger:
    """Logger for Dispatch CLI with Rich integration and verbosity control."""

    def __init__(self, verbose: bool = False):
        """Initialize logger.

        Args:
            verbose: If True, show all messages including debug. If False, only show important messages.
        """
        self.verbose = verbose
        self.console = Console()
        self._live_context: Live | None = None
        self._current_status: str | None = None
        # Detect if we're running in a pipe (e.g., called by MCP tool)
        # When piped, use plain text and flush immediately for better interop
        self._is_piped = not sys.stdout.isatty()

    def _print(
        self,
        message: str | Table | Panel,
        plain_prefix: str = "",
        **kwargs,
    ):
        """Internal print method that handles piped vs TTY output.

        Args:
            message: Rich-formatted message, Table, or Panel for TTY output
            plain_prefix: Plain text prefix for piped output (e.g., "WARNING: ")
            **kwargs: Extra fields for Rich console
        """
        if self._is_piped:
            # Render any Rich object to plain text
            string_io = StringIO()
            plain_console = Console(file=string_io, force_terminal=False, no_color=True)
            plain_console.print(message)
            plain = string_io.getvalue().rstrip("\n")
            print(f"{plain_prefix}{plain}", file=sys.stderr, flush=True)
        else:
            self.console.print(message, **kwargs)

    def debug(self, message: str, **kwargs):
        """Debug message - only shown in verbose mode.

        Args:
            message: Message to log
            **kwargs: Extra fields to include in output
        """
        if self.verbose:
            self._print(f"[dim]  → {message}[/dim]", plain_prefix="DEBUG: ", **kwargs)

    def info(self, message: str, **kwargs):
        """Info message - always shown.

        Args:
            message: Message to log
            **kwargs: Extra fields to include in output
        """
        self._print(message, **kwargs)

    def success(self, message: str, **kwargs):
        """Success message - always shown with green checkmark.

        Args:
            message: Message to log
            **kwargs: Extra fields to include in output
        """
        self._print(f"[green]✓[/green] {message}", plain_prefix="SUCCESS: ", **kwargs)

    def warning(self, message: str, **kwargs):
        """Warning message - always shown in yellow.

        Args:
            message: Message to log
            **kwargs: Extra fields to include in output
        """
        self._print(
            f"[yellow]⚠[/yellow]  {message}", plain_prefix="WARNING: ", **kwargs
        )

    def error(self, message: str, **kwargs):
        """Error message - always shown in red.

        Args:
            message: Message to log
            **kwargs: Extra fields to include in output
        """
        self._print(
            f"[bold red]✗[/bold red] {message}", plain_prefix="ERROR: ", **kwargs
        )

    def status(self, message: str):
        """Update status line.

        In non-verbose mode: Updates a single status line (with Live context)
        In verbose mode: Prints each status as a debug message
        In piped mode: Prints each status as a plain message

        Args:
            message: Status message to display
        """
        if self._is_piped:
            # Piped mode: print status updates for subprocess consumers
            print(f"STATUS: {message}", flush=True)
        elif self.verbose:
            # In verbose mode, print each status update as debug
            self.debug(message)
        elif self._live_context:
            # In non-verbose mode with Live context, update the status line
            spinner = Spinner("dots", text=message)
            self._live_context.update(spinner)

    def code(self, code: str, language: str = "bash", title: str | None = None):
        """Display code as plain text for easy copy-paste.

        Uses raw print() to bypass Rich's word wrapping entirely.

        Args:
            code: Code to display
            language: Ignored (kept for API compatibility)
            title: Optional title to print above the code
        """
        _ = language  # Unused, kept for API compatibility

        if title:
            self._print(f"[dim]{title}[/dim]")

        # Use raw print() to bypass Rich completely - no wrapping!
        for line in code.split("\n"):
            print(line, flush=True)

        print(flush=True)  # Blank line after code

    def table(self, table: Table):
        """Display a Rich table.

        Args:
            table: Rich Table object to display
        """
        self._print(table)

    def panel(self, content: str, title: str | None = None, style: str = "cyan"):
        """Display content in a bordered panel.

        Args:
            content: Content to display
            title: Optional title for the panel
            style: Border style (color)
        """
        self._print(Panel(content, title=title, border_style=style))

    @contextmanager
    def status_context(self, initial_message: str = "Working..."):
        """Context manager for status updates.

        In non-verbose mode: Shows a single updating status line with spinner
        In verbose mode: Prints each status update as it happens
        In piped mode: Prints each status update as plain text

        Usage:
            with logger.status_context("Deploying agent..."):
                logger.status("Building image...")
                # do work
                logger.status("Pushing to registry...")
                # do work
                logger.status("Starting container...")

        Args:
            initial_message: Initial status message
        """
        if self._is_piped or self.verbose:
            # Piped/verbose mode: just print updates, no Live context needed
            self.status(initial_message)
            yield
        else:
            # Non-verbose mode: use Live context for single-line updates
            spinner = Spinner("dots", text=initial_message)
            with Live(spinner, console=self.console, refresh_per_second=10) as live:
                self._live_context = live
                try:
                    yield
                finally:
                    self._live_context = None

    def section(self, title: str):
        """Print a section header.

        Args:
            title: Section title
        """
        self._print("")
        self._print(f"[bold cyan]{title}[/bold cyan]")
        self._print("")


# Global logger instance (set by CLI main)
_logger: DispatchLogger | None = None


def get_logger() -> DispatchLogger:
    """Get the global logger instance.

    Returns the configured global logger, or a default instance if set_logger()
    has not been called yet (e.g. when auth modules are used before CLI startup).

    Returns:
        Global DispatchLogger instance
    """
    if _logger is None:
        return DispatchLogger()
    return _logger


def set_logger(verbose: bool = False):
    """Initialize the global logger.

    This should be called once in the main CLI entry point.

    Args:
        verbose: Enable verbose mode (show debug messages)
    """
    global _logger
    _logger = DispatchLogger(verbose=verbose)
