"""
IOC module for Falcon MCP Server.

This module provides tools for searching, creating, and deleting custom IOCs
using Falcon IOC Service Collection endpoints.
"""

from textwrap import dedent
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.ioc import SEARCH_IOCS_FQL_DOCUMENTATION

logger = get_logger(__name__)


class IOCModule(BaseModule):
    """Module for managing custom IOCs."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.search_iocs,
            name="search_iocs",
        )

        self._add_tool(
            server=server,
            method=self.add_ioc,
            name="add_ioc",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.remove_iocs,
            name="remove_iocs",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        search_iocs_fql_resource = TextResource(
            uri=AnyUrl("falcon://ioc/search/fql-guide"),
            name="falcon_search_iocs_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_iocs` tool.",
            text=SEARCH_IOCS_FQL_DOCUMENTATION,
        )

        self._add_resource(
            server,
            search_iocs_fql_resource,
        )

    def search_iocs(
        self,
        filter: str | None = None,  # was: Field(default=None)
        limit: int = 10,  # was: Field(default=10, ge=1, le=500)
        offset: int = None,  # was: Field(default=None); offset: int | None
        sort: str | None = None,  # was: Field(default=None)
        after: str | None = None,  # was: Field(default=None)
        from_parent: bool = None,  # was: Field(default=None); from_parent: bool | None
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search custom IOCs and return full IOC details.

        IMPORTANT: You must use the `falcon://ioc/search/fql-guide` resource
        when you need to use the `filter` parameter.

        Args:
            filter: FQL filter to limit IOC search results. IMPORTANT: use the `falcon://ioc/search/fql-guide` resource when building this filter parameter.
                Examples: {"type:'domain'+expired:false", "source:'mcp'"}
            limit: Maximum number of IOC IDs to return from search. (Max: 500)
            offset: Starting index of overall result set from which to return IDs.
            sort: Sort IOCs using FQL sort syntax.

                Common fields include:
                action, applied_globally, created_on, expiration, modified_on,
                severity_number, source, type, value

                Supported formats: 'field.asc', 'field.desc', 'field|asc', 'field|desc'
                Examples: 'modified_on.desc', 'severity_number|desc'
                Examples: {"modified_on.desc", "severity_number|desc"}
            after: Pagination token for large result sets. Use the `after` value returned by the previous search call.
            from_parent: Return indicators from the MSSP parent when applicable.
        """
        indicator_ids = self._base_search_api_call(
            operation="indicator_search_v1",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "after": after,
                "from_parent": from_parent,
            },
            error_message="Failed to search IOCs",
        )

        if self._is_error(indicator_ids):
            return self._format_fql_error_response(
                [indicator_ids], filter, SEARCH_IOCS_FQL_DOCUMENTATION
            )

        if not indicator_ids:
            return self._format_fql_error_response([], filter, SEARCH_IOCS_FQL_DOCUMENTATION)

        details = self._base_get_by_ids(
            operation="indicator_get_v1",
            ids=indicator_ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def add_ioc(
        self,
        type: str | None = None,  # was: Field(default=None)
        value: str | None = None,  # was: Field(default=None)
        action: str = "detect",  # was: Field(default="detect")
        source: str = "mcp",  # was: Field(default="mcp")
        severity: str | None = None,  # was: Field(default=None)
        description: str | None = None,  # was: Field(default=None)
        expiration: str | None = None,  # was: Field(default=None)
        applied_globally: bool = None,  # was: Field(default=None); applied_globally: bool | None
        mobile_action: str | None = None,  # was: Field(default=None)
        platforms: list = None,  # was: Field(default=None); platforms: list[str] | None
        host_groups: list = None,  # was: Field(default=None); host_groups: list[str] | None
        tags: list = None,  # was: Field(default=None); tags: list[str] | None
        metadata: dict = None,  # was: Field(default=None); metadata: dict[str, Any] | None
        filename: str | None = None,  # was: Field(default=None)
        comment: str | None = None,  # was: Field(default=None)
        indicators: list = None,  # was: Field(default=None); indicators: list[dict[str, Any]] | None
        ignore_warnings: bool = False,  # was: Field(default=False)
        retrodetects: bool = None,  # was: Field(default=None); retrodetects: bool | None
    ) -> list[dict[str, Any]]:
        """Create one or more custom IOCs.

        Args:
            type: IOC type for single IOC creation. Common values: domain, ipv4, ipv6, md5, sha256. Required when `indicators` is not provided.
            value: IOC value for single IOC creation. Required when `indicators` is not provided.
            action: Action for single IOC creation. Example values: detect, prevent, no_action.
            source: Source label for the IOC.
            severity: Severity label for single IOC creation.
            description: Description text for single IOC creation.
            expiration: Expiration timestamp in UTC (ISO 8601). Example: 2026-12-31T23:59:59Z
            applied_globally: Whether the IOC is applied globally.
            mobile_action: Action to apply on mobile platforms.
            platforms: Platform list for single IOC creation.
            host_groups: Host groups for scoped IOC application.
            tags: Falcon grouping tags to attach to the IOC.
            metadata: Metadata dictionary for the IOC. Example: {'filename': 'evil.exe'}
            filename: Convenience shortcut for metadata filename. Merged into `metadata`.
            comment: Audit comment for IOC creation.
            indicators: Optional bulk IOC payload. If provided, single IOC fields are ignored.
            ignore_warnings: Set to true to ignore warnings and create all submitted IOCs.
            retrodetects: Whether to submit IOCs to retrodetect processing.
        """
        payload_or_error = self._build_add_ioc_payload(
            type=type,
            value=value,
            action=action,
            source=source,
            severity=severity,
            description=description,
            expiration=expiration,
            applied_globally=applied_globally,
            mobile_action=mobile_action,
            platforms=platforms,
            host_groups=host_groups,
            tags=tags,
            metadata=metadata,
            filename=filename,
            comment=comment,
            indicators=indicators,
        )

        if self._is_error(payload_or_error):
            return [payload_or_error]

        result = self._base_query_api_call(
            operation="indicator_create_v1",
            query_params={
                "ignore_warnings": ignore_warnings,
                "retrodetects": retrodetects,
            },
            body_params=payload_or_error,
            error_message="Failed to add IOC",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def remove_iocs(
        self,
        ids: list = None,  # was: Field(default=None); ids: list[str] | None
        filter: str | None = None,  # was: Field(default=None)
        comment: str | None = None,  # was: Field(default=None)
        from_parent: bool = None,  # was: Field(default=None); from_parent: bool | None
    ) -> list[dict[str, Any]]:
        """Remove custom IOCs by IDs or FQL filter.

        Args:
            ids: IOC IDs to remove. Use this when deleting specific IOCs.
            filter: FQL expression for bulk IOC removal. If both `filter` and `ids` are provided, `filter` takes precedence.
            comment: Audit comment describing why these IOCs are being removed.
            from_parent: Limit action to IOCs originating from the MSSP parent.
        """
        if not ids and not filter:
            return [
                _format_error_response(
                    "Either `ids` or `filter` must be provided to remove IOCs.",
                    operation="indicator_delete_v1",
                )
            ]

        result = self._base_query_api_call(
            operation="indicator_delete_v1",
            query_params={
                "ids": ids,
                "filter": filter,
                "comment": comment,
                "from_parent": from_parent,
            },
            error_message="Failed to remove IOCs",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def _build_add_ioc_payload(
        self,
        type: str | None,
        value: str | None,
        action: str,
        source: str,
        severity: str | None,
        description: str | None,
        expiration: str | None,
        applied_globally: bool | None,
        mobile_action: str | None,
        platforms: list[str] | None,
        host_groups: list[str] | None,
        tags: list[str] | None,
        metadata: dict[str, Any] | None,
        filename: str | None,
        comment: str | None,
        indicators: list[dict[str, Any]] | None,
    ) -> dict[str, Any]:
        """Build IOC create payload or return a validation error payload."""
        if indicators:
            payload: dict[str, Any] = {"indicators": indicators}
            if comment:
                payload["comment"] = comment
            return payload

        if not type or not value:
            return _format_error_response(
                "`type` and `value` are required when `indicators` is not provided.",
                operation="indicator_create_v1",
            )

        indicator: dict[str, Any] = {
            "type": type,
            "value": value,
            "action": action,
            "source": source,
        }

        optional_values = {
            "severity": severity,
            "description": description,
            "expiration": expiration,
            "applied_globally": applied_globally,
            "mobile_action": mobile_action,
            "platforms": platforms,
            "host_groups": host_groups,
            "tags": tags,
        }
        for key, value_ in optional_values.items():
            if value_ is not None:
                indicator[key] = value_

        if metadata:
            indicator["metadata"] = metadata
        if filename:
            existing_metadata = indicator.get("metadata", {})
            if not isinstance(existing_metadata, dict):
                existing_metadata = {}
            existing_metadata["filename"] = filename
            indicator["metadata"] = existing_metadata

        payload = {"indicators": [indicator]}
        if comment:
            payload["comment"] = comment

        return payload
