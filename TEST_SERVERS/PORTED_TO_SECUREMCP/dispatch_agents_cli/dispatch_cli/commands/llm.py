"""LLM configuration and testing commands."""

import os
from typing import Annotated, Any

import questionary
import requests
import typer

from dispatch_cli.auth import get_auth_headers, handle_auth_error
from dispatch_cli.logger import get_logger
from dispatch_cli.secrets import add_secret as add_local_secret

from .agent import build_namespaced_url
from .secrets import _NAMESPACE_SOURCE_DISPLAY, get_namespace_from_config

# Maps provider to the env var name used by the provider SDK
PROVIDER_ENV_VARS = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
}

llm_app = typer.Typer(
    name="llm",
    help="Configure and test LLM providers",
    rich_markup_mode="markdown",
)

# Valid provider formats
VALID_PROVIDER_FORMATS = ["openai", "anthropic"]

# Default models per provider
DEFAULT_MODELS = {
    "openai": "gpt-5",
    "anthropic": "claude-sonnet-4-5-20250929",
}

# Popular models per provider for the setup wizard (2026)
POPULAR_MODELS: dict[str, list[str]] = {
    "openai": [
        "gpt-5",
        "gpt-4.1",
        "gpt-4.1-mini",
        "gpt-4.1-nano",
        "o3",
        "o3-mini",
        "o4-mini",
        "gpt-4o",
    ],
    "anthropic": [
        "claude-sonnet-4-5-20250929",
        "claude-opus-4-20250514",
        "claude-haiku-4-5-20251001",
    ],
}

# Providers shown in the interactive setup wizard
SETUP_WIZARD_PROVIDERS = ["openai", "anthropic"]


def _resolve_namespace(namespace: str | None, logger: Any) -> str:
    """Resolve namespace from config and log the source."""
    resolved_namespace, namespace_source = get_namespace_from_config(
        namespace, verify=True
    )
    logger.info(
        f"Using namespace: [bold]{resolved_namespace}[/bold] "
        f"[dim](from {_NAMESPACE_SOURCE_DISPLAY[namespace_source]})[/dim]"
    )
    return resolved_namespace


@llm_app.command("configure")
def configure_provider(
    provider: Annotated[
        str,
        typer.Argument(
            help=f"LLM provider to configure. Options: {', '.join(VALID_PROVIDER_FORMATS)}"
        ),
    ],
    api_key: Annotated[
        str | None,
        typer.Option(
            "--api-key",
            "-k",
            help="API key for the provider (will prompt if not provided)",
        ),
    ] = None,
    model: Annotated[
        str | None,
        typer.Option("--model", "-m", help="Default model for this provider"),
    ] = None,
    secret_path: Annotated[
        str | None,
        typer.Option(
            "--secret-path",
            help="Custom secret path (default: llm/{provider}-api-key)",
        ),
    ] = None,
    set_default: Annotated[
        bool,
        typer.Option("--default", "-d", help="Set as default provider"),
    ] = False,
    namespace: Annotated[
        str | None,
        typer.Option(
            help="Namespace (defaults to dispatch.yaml or DISPATCH_NAMESPACE)",
            envvar="DISPATCH_NAMESPACE",
        ),
    ] = None,
):
    """Configure an LLM provider with API key and default model.

    This command:
    1. Uploads your API key to secure storage
    2. Configures the provider with model settings
    3. Optionally sets it as your default provider

    Examples:
        dispatch llm configure openai --api-key sk-proj-...
        dispatch llm configure anthropic --default
        dispatch llm configure openai --model gpt-4-turbo
    """
    logger = get_logger()

    if provider not in VALID_PROVIDER_FORMATS:
        logger.error(f"Invalid provider '{provider}'")
        logger.info(f"Valid providers: {', '.join(VALID_PROVIDER_FORMATS)}")
        raise typer.Exit(1)

    resolved_namespace = _resolve_namespace(namespace, logger)

    # Prompt for API key if not provided
    if not api_key:
        api_key_env = os.environ.get(f"{provider.upper()}_API_KEY")
        if api_key_env:
            use_env = typer.confirm(
                f"Found {provider.upper()}_API_KEY in environment. Use it?"
            )
            api_key = (
                api_key_env
                if use_env
                else questionary.password(f"Enter your {provider} API key:").ask()
            )
        else:
            api_key = questionary.password(f"Enter your {provider} API key:").ask()

    if not api_key or not api_key.strip():
        logger.error("API key cannot be empty")
        raise typer.Exit(1)

    api_key = api_key.strip()
    if not model:
        model = DEFAULT_MODELS.get(provider, "")
        logger.info(f"Using default model: [bold]{model}[/bold]")
    if not secret_path:
        secret_path = f"llm/{provider}-api-key"

    auth_headers = get_auth_headers()

    # Use the single-step /setup endpoint
    logger.info(f"\nConfiguring {provider} provider...")
    try:
        response = requests.post(
            build_namespaced_url(
                f"/llm-config/providers/{provider}/setup", resolved_namespace
            ),
            json={
                "api_key": api_key,
                "default_model": model,
                "scope": "org",
                "set_default": set_default,
                "allow_overwrite": False,
                "base_provider": provider,
            },
            headers=auth_headers,
            timeout=30,
        )
        if response.status_code == 401:
            handle_auth_error("Invalid or expired API key")
        response.raise_for_status()
        logger.success(f"Provider '{provider}' configured with model '{model}'")
        if set_default:
            logger.success(f"'{provider}' set as default provider")
    except requests.exceptions.HTTPError as e:
        logger.error(f"Failed to configure provider: {e}")
        if e.response:
            try:
                detail = e.response.json().get("detail", "")
                if detail:
                    logger.error(f"  Details: {detail}")
            except Exception:
                pass
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Failed to configure provider: {e}")
        raise typer.Exit(1)

    # Summary
    logger.info("\n" + "─" * 50)
    logger.success(f"LLM provider '{provider}' configured successfully!")
    logger.info(f"  • Secret path: {secret_path}")
    logger.info(f"  • Default model: {model}")
    logger.info(f"  • Is default: {'Yes' if set_default else 'No'}")
    logger.info("\nYou can now use the LLM gateway in your agents:")
    logger.code(
        """from dispatch_agents import llm

response = await llm.inference([
    {"role": "user", "content": "Hello!"}
])
print(response.content)""",
        "python",
    )


@llm_app.command("list")
def list_providers(
    namespace: Annotated[
        str | None,
        typer.Option(
            help="Namespace (defaults to dispatch.yaml or DISPATCH_NAMESPACE)",
            envvar="DISPATCH_NAMESPACE",
        ),
    ] = None,
):
    """List configured LLM providers."""
    logger = get_logger()
    resolved_namespace = _resolve_namespace(namespace, logger)
    auth_headers = get_auth_headers()

    try:
        with logger.status_context("Fetching LLM configuration..."):
            response = requests.get(
                build_namespaced_url("/llm-config/providers", resolved_namespace),
                headers=auth_headers,
                timeout=30,
            )
            response.raise_for_status()

        config = response.json()
        providers = config.get("providers", {})
        default_provider = config.get("default_provider")

        if not providers:
            logger.warning("No LLM providers configured")
            logger.info("\nTo configure a provider, run:")
            logger.code("dispatch llm configure openai --api-key sk-...", "bash")
            return

        logger.info("\n[bold]Configured LLM Providers:[/bold]")
        for name, provider_config in providers.items():
            is_default = name == default_provider
            default_marker = " [green](default)[/green]" if is_default else ""
            enabled = provider_config.get("enabled", True)
            status = "[green]enabled[/green]" if enabled else "[red]disabled[/red]"

            logger.info(f"\n  [bold]{name}[/bold]{default_marker}")
            logger.info(f"    Status: {status}")
            logger.info(f"    Model: {provider_config.get('default_model', 'N/A')}")
            logger.info(f"    Secret: {provider_config.get('secret_path', 'N/A')}")

        logger.info(f"\n[dim]Total: {len(providers)} provider(s)[/dim]")

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            handle_auth_error("Invalid or expired credential")
        else:
            logger.error(f"Failed to fetch providers: {e}")
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Failed to fetch providers: {e}")
        raise typer.Exit(1)


@llm_app.command("test")
def test_llm(
    prompt: Annotated[
        str,
        typer.Argument(help="Prompt to send to the LLM"),
    ] = "Say hello in exactly 5 words.",
    provider: Annotated[
        str | None,
        typer.Option(
            "--provider", "-p", help="Provider to use (uses default if not set)"
        ),
    ] = None,
    model: Annotated[
        str | None,
        typer.Option(
            "--model", "-m", help="Model to use (uses provider default if not set)"
        ),
    ] = None,
    namespace: Annotated[
        str | None,
        typer.Option(
            help="Namespace (defaults to dispatch.yaml or DISPATCH_NAMESPACE)",
            envvar="DISPATCH_NAMESPACE",
        ),
    ] = None,
):
    """Test the LLM gateway with a simple prompt.

    Examples:
        dispatch llm test
        dispatch llm test "What is 2+2?"
        dispatch llm test --provider anthropic "Hello!"
    """
    logger = get_logger()
    resolved_namespace = _resolve_namespace(namespace, logger)
    auth_headers = get_auth_headers()

    # Build request payload
    payload: dict = {
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }
    if provider:
        payload["provider"] = provider
    if model:
        payload["model"] = model

    logger.info(f"\n[bold]Prompt:[/bold] {prompt}")
    if provider:
        logger.info(f"[bold]Provider:[/bold] {provider}")
    if model:
        logger.info(f"[bold]Model:[/bold] {model}")
    logger.info("")

    try:
        with logger.status_context("Waiting for LLM response..."):
            response = requests.post(
                build_namespaced_url("/llm/inference", resolved_namespace),
                json=payload,
                headers=auth_headers,
                timeout=120,  # LLM calls can take a while
            )
            response.raise_for_status()

        result = response.json()

        # Display response
        logger.info("[bold]Response:[/bold]")
        logger.info(f"  {result.get('content', 'No content')}")

        # Display metrics
        logger.info("\n[bold]Metrics:[/bold]")
        logger.info(f"  Model: {result.get('model', 'N/A')}")
        logger.info(f"  Provider: {result.get('provider', 'N/A')}")
        logger.info(f"  Input tokens: {result.get('input_tokens', 0)}")
        logger.info(f"  Output tokens: {result.get('output_tokens', 0)}")
        logger.info(f"  Cost: ${result.get('cost_usd', 0):.6f}")
        logger.info(f"  Latency: {result.get('latency_ms', 0)}ms")

        logger.success("\nLLM gateway is working correctly!")

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            handle_auth_error("Invalid or expired credential")
        elif e.response.status_code == 400:
            try:
                detail = e.response.json().get("detail", "")
                logger.error(f"Bad request: {detail}")
            except Exception as parse_err:
                logger.debug(f"Could not parse error response: {parse_err}")
                logger.error(f"Bad request: {e}")
        else:
            logger.error(f"LLM inference failed: {e}")
            try:
                detail = e.response.json().get("detail", "")
                if detail:
                    logger.error(f"  Details: {detail}")
            except Exception as parse_err:
                logger.debug(f"Could not parse error response: {parse_err}")
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f"LLM inference failed: {e}")
        raise typer.Exit(1)


@llm_app.command("set-default")
def set_default_provider(
    provider: Annotated[
        str,
        typer.Argument(help="Provider to set as default"),
    ],
    namespace: Annotated[
        str | None,
        typer.Option(
            help="Namespace (defaults to dispatch.yaml or DISPATCH_NAMESPACE)",
            envvar="DISPATCH_NAMESPACE",
        ),
    ] = None,
):
    """Set the default LLM provider.

    Example:
        dispatch llm set-default anthropic
    """
    logger = get_logger()
    resolved_namespace = _resolve_namespace(namespace, logger)
    auth_headers = get_auth_headers()

    try:
        with logger.status_context(f"Setting {provider} as default..."):
            response = requests.post(
                build_namespaced_url(
                    "/llm-config/default-provider", resolved_namespace
                ),
                json={"provider": provider},
                headers=auth_headers,
                timeout=30,
            )
            response.raise_for_status()

        logger.success(f"'{provider}' is now the default LLM provider")

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            handle_auth_error("Invalid or expired credential")
        elif e.response.status_code == 400:
            try:
                detail = e.response.json().get("detail", "")
                logger.error(f"Error: {detail}")
            except Exception as parse_err:
                logger.debug(f"Could not parse error response: {parse_err}")
                logger.error(f"Bad request: {e}")
        else:
            logger.error(f"Failed to set default: {e}")
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Failed to set default: {e}")
        raise typer.Exit(1)


@llm_app.command("delete")
def delete_provider(
    provider: Annotated[
        str,
        typer.Argument(help="Provider to delete"),
    ],
    namespace: Annotated[
        str | None,
        typer.Option(
            help="Namespace (defaults to dispatch.yaml or DISPATCH_NAMESPACE)",
            envvar="DISPATCH_NAMESPACE",
        ),
    ] = None,
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Skip confirmation prompt"),
    ] = False,
):
    """Delete an LLM provider configuration.

    Note: This does NOT delete the API key from secrets storage.

    Example:
        dispatch llm delete openai
    """
    logger = get_logger()
    resolved_namespace = _resolve_namespace(namespace, logger)

    if not force:
        confirmed = typer.confirm(
            f"Are you sure you want to delete provider '{provider}'?"
        )
        if not confirmed:
            logger.info("Cancelled")
            return

    auth_headers = get_auth_headers()

    try:
        with logger.status_context(f"Deleting {provider}..."):
            response = requests.delete(
                build_namespaced_url(
                    f"/llm-config/providers/{provider}", resolved_namespace
                ),
                headers=auth_headers,
                timeout=30,
            )
            response.raise_for_status()

        logger.success(f"Provider '{provider}' deleted")
        logger.info(
            "\n[dim]Note: The API key is still in secrets storage. "
            "Delete it separately if needed.[/dim]"
        )

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            handle_auth_error("Invalid or expired credential")
        elif e.response.status_code == 404:
            logger.error(f"Provider '{provider}' not found")
        else:
            logger.error(f"Failed to delete provider: {e}")
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Failed to delete provider: {e}")
        raise typer.Exit(1)


def _try_validate_key(
    api_key: str,
    provider: str,
    namespace: str,
    auth_headers: dict[str, str],
    base_provider: str | None = None,
    base_url: str | None = None,
) -> bool | None:
    """Validate an API key against the backend. Returns True/False, or None if unreachable."""
    log = get_logger()
    payload: dict[str, Any] = {
        "api_key": api_key,
        "base_provider": base_provider or provider,
    }
    if base_url:
        payload["base_url"] = base_url
    try:
        resp = requests.post(
            build_namespaced_url(
                f"/llm-config/providers/{provider}/validate", namespace
            ),
            json=payload,
            headers=auth_headers,
            timeout=15,
        )
        if resp.ok:
            result = resp.json()
            return bool(result.get("valid"))
    except requests.exceptions.RequestException:
        log.warning("Could not reach backend for validation. Proceeding...")
    return None


def _validate_api_key_with_retry(
    api_key: str,
    provider: str,
    namespace: str,
    auth_headers: dict[str, str],
    base_provider: str | None = None,
    base_url: str | None = None,
) -> str:
    """Validate an API key, offering one retry on failure. Returns the (possibly new) key."""

    log = get_logger()

    valid = _try_validate_key(
        api_key, provider, namespace, auth_headers, base_provider, base_url
    )
    if valid is None:
        return api_key  # Backend unreachable, proceed
    if valid:
        log.success("API key validated successfully")
        return api_key

    log.error(f"API key validation failed for {provider}")
    retry = questionary.confirm(
        "Would you like to enter a different key?", default=True
    ).ask()
    if not retry:
        log.warning("Proceeding with unvalidated key...")
        return api_key

    new_key = questionary.password(f"Enter your {provider} API key:").ask()
    if not new_key or not new_key.strip():
        log.error("API key cannot be empty")
        raise typer.Exit(1)
    new_key = new_key.strip()

    retry_valid = _try_validate_key(
        new_key, provider, namespace, auth_headers, base_provider, base_url
    )
    if retry_valid:
        log.success("API key validated successfully")
    elif retry_valid is False:
        log.warning("Key validation still failed. Proceeding anyway...")
    return new_key


@llm_app.command("setup")
def setup_wizard(
    provider: Annotated[
        str | None,
        typer.Argument(
            help="LLM provider to configure (e.g., openai, anthropic, or a custom name)",
        ),
    ] = None,
    namespace: Annotated[
        str | None,
        typer.Option(
            help="Namespace (defaults to dispatch.yaml or DISPATCH_NAMESPACE)",
            envvar="DISPATCH_NAMESPACE",
        ),
    ] = None,
):
    """Interactive wizard to set up an LLM provider.

    Walks you through configuring a provider with API key, model selection,
    scope, and local dev storage.

    Examples:
        dispatch llm setup
        dispatch llm setup openai
    """

    logger = get_logger()

    logger.info("\n[bold]Welcome to Dispatch LLM Setup![/bold]\n")

    # Step 1: Select provider
    is_custom = False
    custom_base_provider: str | None = None
    custom_base_url: str | None = None

    if not provider:
        provider = questionary.select(
            "Which provider would you like to configure?",
            choices=[
                *SETUP_WIZARD_PROVIDERS,
                questionary.Choice("Custom provider", value="_custom"),
            ],
            default="openai",
        ).ask()
        if not provider:
            raise typer.Exit(1)

    if provider == "_custom":
        provider = questionary.text(
            "Provider name (e.g., 'my-vllm-server', 'together-ai'):"
        ).ask()
        if not provider:
            raise typer.Exit(1)
        provider = provider.strip().lower()
        is_custom = True

    if provider not in VALID_PROVIDER_FORMATS:
        is_custom = True

    if is_custom:
        custom_base_provider = questionary.select(
            "API format (how does this provider accept requests)?",
            choices=[
                questionary.Choice("OpenAI-compatible", value="openai"),
                questionary.Choice("Anthropic-compatible", value="anthropic"),
            ],
            default="openai",
        ).ask()
        if not custom_base_provider:
            raise typer.Exit(1)

        custom_base_url = questionary.text(
            "Base URL (everything before /v1, e.g., https://api.together.xyz):"
        ).ask()
        if not custom_base_url or not custom_base_url.strip():
            logger.error("Base URL is required for custom providers")
            raise typer.Exit(1)
        custom_base_url = custom_base_url.strip().rstrip("/")

    # Step 2: Where should the key be available?
    storage = questionary.select(
        "Where should this key be available?",
        choices=[
            questionary.Choice(
                "Both local dev and deployed agents (Recommended)", value="both"
            ),
            questionary.Choice("Local development only", value="local"),
            questionary.Choice("Deployed agents only", value="remote"),
        ],
        default="both",
    ).ask()
    if not storage:
        raise typer.Exit(1)

    store_local = storage in ("both", "local")
    store_remote = storage in ("both", "remote")

    # Step 3: If deploying remotely, pick scope and check for existing config
    remote_scope = "org"
    resolved_namespace = None
    auth_headers: dict[str, str] = {}
    model = None
    set_default = False
    if store_remote:
        resolved_namespace = _resolve_namespace(namespace, logger)
        auth_headers = get_auth_headers()

        scope = questionary.select(
            "Configuration scope:",
            choices=[
                questionary.Choice("Organization-wide (Recommended)", value="org"),
                questionary.Choice(
                    f"Namespace only ({resolved_namespace})", value="namespace"
                ),
            ],
            default="org",
        ).ask()
        if not scope:
            raise typer.Exit(1)
        remote_scope = scope

        # Check if provider already exists at this scope — block overwrite
        try:
            if remote_scope == "org":
                check_resp = requests.get(
                    build_namespaced_url(
                        "/llm-config/org-providers", resolved_namespace
                    ),
                    headers=auth_headers,
                    timeout=10,
                )
            else:
                check_resp = requests.get(
                    build_namespaced_url("/llm-config/providers", resolved_namespace),
                    params={"resolved": "false"},
                    headers=auth_headers,
                    timeout=10,
                )
            if check_resp.ok:
                existing = check_resp.json().get("providers", {})
                if provider in existing:
                    logger.error(
                        f"Provider '{provider}' is already configured "
                        f"at {remote_scope} scope."
                    )
                    logger.info(
                        "To update an existing provider's API key, "
                        "use the web UI at /manage/llm-providers."
                    )
                    raise typer.Exit(1)
        except requests.exceptions.RequestException:
            pass  # Best-effort — proceed if we can't reach the backend
        except typer.Exit:
            raise
        except Exception:
            pass

        # Model selection
        models = POPULAR_MODELS.get(provider, [])
        if models:
            default_model = DEFAULT_MODELS.get(provider, "")
            model_choices = [questionary.Choice(m, value=m) for m in models]
            model_choices.append(
                questionary.Choice("Other (enter manually)", value="_other")
            )

            model = questionary.select(
                "Default model:",
                choices=model_choices,
                default=default_model if default_model in models else None,
            ).ask()
            if not model:
                raise typer.Exit(1)
            if model == "_other":
                model = questionary.text("Enter model name:").ask()
                if not model or not model.strip():
                    logger.error("Model name cannot be empty")
                    raise typer.Exit(1)
                model = model.strip()
        else:
            # Custom provider — no preset list, just ask
            model = questionary.text("Default model name:").ask()
            if not model or not model.strip():
                logger.error("Model name cannot be empty")
                raise typer.Exit(1)
            model = model.strip()

        set_default = questionary.confirm(
            "Set as default provider?", default=True
        ).ask()
        if set_default is None:
            raise typer.Exit(1)

    # Step 4: Get API key (last — after all other questions are answered)
    env_var = PROVIDER_ENV_VARS.get(provider, f"{provider.upper()}_API_KEY")
    api_key_env = os.environ.get(env_var)
    if api_key_env:
        use_env = questionary.confirm(
            f"Found {env_var} in environment. Use it?", default=True
        ).ask()
        if use_env is None:
            raise typer.Exit(1)
        api_key = (
            api_key_env
            if use_env
            else questionary.password(f"Enter your {provider} API key:").ask()
        )
    else:
        api_key = questionary.password(f"Enter your {provider} API key:").ask()

    if not api_key or not api_key.strip():
        logger.error("API key cannot be empty")
        raise typer.Exit(1)
    api_key = api_key.strip()

    # Validate API key before saving
    if store_remote and resolved_namespace:
        api_key = _validate_api_key_with_retry(
            api_key,
            provider,
            resolved_namespace,
            auth_headers,
            base_provider=custom_base_provider,
            base_url=custom_base_url,
        )

    logger.info("")

    # Execute: store locally
    if store_local:
        try:
            success = add_local_secret(env_var, api_key, use_keychain=True)
            if success:
                logger.success(f"API key stored locally (macOS Keychain: {env_var})")
            else:
                logger.warning("Failed to store locally, trying without Keychain...")
                add_local_secret(env_var, api_key, use_keychain=False)
                logger.success(f"API key stored locally ({env_var})")
        except Exception as e:
            logger.warning(f"Could not store locally: {e}")

    # Execute: store remotely via /setup endpoint
    if store_remote:
        assert resolved_namespace is not None
        setup_payload: dict[str, Any] = {
            "api_key": api_key,
            "default_model": model,
            "scope": remote_scope,
            "set_default": set_default,
            "allow_overwrite": False,
            "base_provider": custom_base_provider if is_custom else provider,
        }
        if custom_base_url:
            setup_payload["base_url"] = custom_base_url

        try:
            response = requests.post(
                build_namespaced_url(
                    f"/llm-config/providers/{provider}/setup", resolved_namespace
                ),
                json=setup_payload,
                headers=auth_headers,
                timeout=30,
            )
            if response.status_code == 401:
                handle_auth_error("Invalid or expired API key")
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to configure remote provider: {e}")
            if e.response:
                try:
                    detail = e.response.json().get("detail", "")
                    if detail:
                        logger.error(f"  Details: {detail}")
                except Exception:
                    pass
            raise typer.Exit(1)
        except Exception as e:
            logger.error(f"Failed to configure remote provider: {e}")
            raise typer.Exit(1)

    # Print final config summary
    logger.info("─" * 50)
    logger.success("LLM setup complete! Here's your configuration:\n")
    logger.info(f"  Provider:   {provider}")
    if is_custom:
        logger.info(f"  Format:     {custom_base_provider}-compatible")
        logger.info(f"  Base URL:   {custom_base_url}")
    if store_local:
        logger.info(f"  Local dev:  {env_var} (stored)")
    if store_remote:
        scope_label = (
            "org-wide" if remote_scope == "org" else f"namespace ({resolved_namespace})"
        )
        logger.info(f"  Deployed:   {scope_label}")
        logger.info(f"  Model:      {model}")
        logger.info(f"  Default:    {'Yes' if set_default else 'No'}")
    logger.info("")
    logger.info("─" * 50)
    logger.info("\nUse LLM in your agents:")
    logger.code(
        """from dispatch_agents import llm

response = await llm.inference([
    {"role": "user", "content": "Hello!"}
])
print(response.content)""",
        "python",
    )


@llm_app.command("local")
def local_provider(
    provider: Annotated[
        str,
        typer.Argument(
            help=f"LLM provider to configure locally. Options: {', '.join(VALID_PROVIDER_FORMATS)}"
        ),
    ],
):
    """Store an LLM provider API key for local development.

    Saves the key to macOS Keychain (or local config) so it's available
    when running `dispatch agent dev`.

    Examples:
        dispatch llm local openai
        dispatch llm local anthropic
    """
    logger = get_logger()

    if provider not in VALID_PROVIDER_FORMATS:
        logger.error(f"Invalid provider '{provider}'")
        logger.info(f"Valid providers: {', '.join(VALID_PROVIDER_FORMATS)}")
        raise typer.Exit(1)

    env_var = PROVIDER_ENV_VARS.get(provider, f"{provider.upper()}_API_KEY")

    # Check environment first
    api_key_env = os.environ.get(env_var)
    if api_key_env:
        use_env = typer.confirm(f"Found {env_var} in environment. Use it?")
        api_key = (
            api_key_env
            if use_env
            else questionary.password(f"Enter your {provider} API key:").ask()
        )
    else:
        api_key = questionary.password(f"Enter your {provider} API key:").ask()

    if not api_key or not api_key.strip():
        logger.error("API key cannot be empty")
        raise typer.Exit(1)

    api_key = api_key.strip()

    try:
        success = add_local_secret(env_var, api_key, use_keychain=True)
        if success:
            logger.success(f"{env_var} stored in macOS Keychain")
        else:
            add_local_secret(env_var, api_key, use_keychain=False)
            logger.success(f"{env_var} stored locally")
    except Exception as e:
        logger.error(f"Failed to store API key: {e}")
        raise typer.Exit(1)

    logger.info("  Available when you run: [bold]dispatch agent dev[/bold]")
