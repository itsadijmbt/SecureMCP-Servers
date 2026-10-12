"""
Custom IOA module for Falcon MCP Server.

This module provides tools for searching, creating, updating, and deleting
Custom IOA (Indicators of Attack) behavioral rules and rule groups using
Falcon Custom IOA Service Collection endpoints.
"""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.custom_ioa import SEARCH_IOA_RULE_GROUPS_FQL_DOCUMENTATION

logger = get_logger(__name__)


class CustomIOAModule(BaseModule):
    """Module for managing Custom IOA behavioral rules and rule groups."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.search_ioa_rule_groups,
            name="search_ioa_rule_groups",
        )

        self._add_tool(
            server=server,
            method=self.get_ioa_platforms,
            name="get_ioa_platforms",
        )

        self._add_tool(
            server=server,
            method=self.get_ioa_rule_types,
            name="get_ioa_rule_types",
        )

        self._add_tool(
            server=server,
            method=self.create_ioa_rule_group,
            name="create_ioa_rule_group",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.update_ioa_rule_group,
            name="update_ioa_rule_group",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.delete_ioa_rule_groups,
            name="delete_ioa_rule_groups",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.create_ioa_rule,
            name="create_ioa_rule",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.update_ioa_rule,
            name="update_ioa_rule",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.delete_ioa_rules,
            name="delete_ioa_rules",
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
        search_rule_groups_fql_resource = TextResource(
            uri=AnyUrl("falcon://custom-ioa/rule-groups/fql-guide"),
            name="falcon_search_ioa_rule_groups_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_ioa_rule_groups` tool.",
            text=SEARCH_IOA_RULE_GROUPS_FQL_DOCUMENTATION,
        )

        self._add_resource(
            server,
            search_rule_groups_fql_resource,
        )

    def search_ioa_rule_groups(
        self,
        filter: str | None = None,  # was: Field(default=None)
        limit: int = 10,  # was: Field(default=10, ge=1, le=500)
        offset: str | None = None,  # was: Field(default=None)
        sort: str | None = None,  # was: Field(default=None)
        q: str | None = None,  # was: Field(default=None)
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search Custom IOA rule groups and return full rule group details including their rules.

        IMPORTANT: You must use the `falcon://custom-ioa/rule-groups/fql-guide` resource
        when you need to use the `filter` parameter.

        Rule groups are containers that hold behavioral detection rules. Each group is
        associated with a specific platform (windows, mac, or linux).

        Args:
            filter: FQL filter to limit rule group search results. IMPORTANT: use the `falcon://custom-ioa/rule-groups/fql-guide` resource when building this filter parameter.
                Examples: {"platform:'windows'+enabled:true", "rules.pattern_severity:'high'"}
            limit: Maximum number of rule groups to return. (Max: 500)
            offset: Starting offset for pagination. Use the offset value from a previous response.
            sort: Sort rule groups using FQL sort syntax. Fields: created_by, created_on, enabled, modified_by, modified_on, name, description. Example: 'modified_on.desc'
                Examples: {"modified_on.desc", "name.asc"}
            q: Free-text match query that searches across all filter string fields.
        """
        result = self._base_search_api_call(
            operation="query_rule_groups_full",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "q": q,
            },
            error_message="Failed to search IOA rule groups",
        )

        if self._is_error(result):
            return self._format_fql_error_response(
                [result], filter, SEARCH_IOA_RULE_GROUPS_FQL_DOCUMENTATION
            )

        if not result:
            return self._format_fql_error_response(
                [], filter, SEARCH_IOA_RULE_GROUPS_FQL_DOCUMENTATION
            )

        return result

    def get_ioa_platforms(self) -> list[dict[str, Any]] | dict[str, Any]:
        """Get all available platforms for Custom IOA rule groups.

        Returns details about each available platform (e.g., windows, mac, linux).
        Use this to discover valid platform values before creating a rule group.
        """
        platform_ids = self._base_search_api_call(
            operation="query_platformsMixin0",
            search_params={},
            error_message="Failed to query IOA platforms",
        )

        if self._is_error(platform_ids):
            return [platform_ids]

        if not platform_ids:
            return []

        details = self._base_get_by_ids(
            operation="get_platformsMixin0",
            ids=platform_ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def get_ioa_rule_types(
        self,
        limit: int = 100,  # was: Field(default=100, ge=1, le=500)
        offset: str | None = None,  # was: Field(default=None)
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Get all available Custom IOA rule types.

        Returns details about each rule type including its name, platform, fields,
        and supported disposition IDs. Use this to discover valid rule type IDs and
        required field values before creating a behavioral rule.

        Rule types define the category of behavioral detection (e.g., Process Creation,
        Network Connection, File Creation).

        Args:
            limit: Maximum number of rule types to return. (Max: 500)
            offset: Starting offset for pagination.
        """
        rule_type_ids = self._base_search_api_call(
            operation="query_rule_types",
            search_params={
                "limit": limit,
                "offset": offset,
            },
            error_message="Failed to query IOA rule types",
        )

        if self._is_error(rule_type_ids):
            return [rule_type_ids]

        if not rule_type_ids:
            return []

        details = self._base_get_by_ids(
            operation="get_rule_types",
            ids=rule_type_ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def create_ioa_rule_group(
        self,
        name: str,  # was: Field()
        platform: str,  # was: Field()
        description: str | None = None,  # was: Field(default=None)
        comment: str | None = None,  # was: Field(default=None)
    ) -> list[dict[str, Any]]:
        """Create a new Custom IOA rule group.

        Rule groups are containers that hold behavioral detection rules for a specific
        platform. After creating a group, use `falcon_create_ioa_rule` to add detection
        rules to it.

        Use `falcon_get_ioa_platforms` to see available platform values.

        Args:
            name: Name for the new rule group.
                Examples: {"Suspicious PowerShell Activity", "Lateral Movement Detection"}
            platform: Platform this rule group applies to. Allowed values: windows, mac, linux.
                Examples: {"windows", "mac", "linux"}
            description: Optional description for the rule group.
            comment: Audit comment explaining why the rule group is being created.
        """
        body: dict[str, Any] = {
            "name": name,
            "platform": platform,
        }
        if description is not None:
            body["description"] = description
        if comment is not None:
            body["comment"] = comment

        result = self._base_query_api_call(
            operation="create_rule_groupMixin0",
            body_params=body,
            error_message="Failed to create IOA rule group",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def update_ioa_rule_group(
        self,
        id: str,  # was: Field()
        rulegroup_version: int,  # was: Field()
        name: str | None = None,  # was: Field(default=None)
        description: str | None = None,  # was: Field(default=None)
        enabled: bool = None,  # was: Field(default=None); enabled: bool | None
        comment: str | None = None,  # was: Field(default=None)
    ) -> list[dict[str, Any]]:
        """Update an existing Custom IOA rule group.

        You can modify the name, description, and enabled state of a rule group.
        The `rulegroup_version` is required for optimistic locking to prevent
        concurrent modification conflicts.

        Use `falcon_search_ioa_rule_groups` to retrieve the current version number.

        Args:
            id: ID of the rule group to update.
            rulegroup_version: Current version of the rule group. Required for optimistic locking. Retrieve this from `falcon_search_ioa_rule_groups`.
            name: New name for the rule group.
            description: New description for the rule group.
            enabled: Whether the rule group should be enabled or disabled.
            comment: Audit comment explaining why the rule group is being updated.
        """
        body: dict[str, Any] = {
            "id": id,
            "rulegroup_version": rulegroup_version,
        }
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if enabled is not None:
            body["enabled"] = enabled
        if comment is not None:
            body["comment"] = comment

        result = self._base_query_api_call(
            operation="update_rule_groupMixin0",
            body_params=body,
            error_message="Failed to update IOA rule group",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def delete_ioa_rule_groups(
        self,
        ids: list,  # was: Field(); ids: list[str]
        comment: str | None = None,  # was: Field(default=None)
    ) -> list[dict[str, Any]]:
        """Delete Custom IOA rule groups by ID.

        This permanently removes the rule groups and all rules within them.
        Use `falcon_search_ioa_rule_groups` to find rule group IDs.

        Args:
            ids: IDs of the rule groups to delete.
            comment: Audit comment explaining why the rule groups are being deleted.
        """
        if not ids:
            return [
                _format_error_response(
                    "`ids` must be provided to delete IOA rule groups.",
                    operation="delete_rule_groupsMixin0",
                )
            ]

        result = self._base_query_api_call(
            operation="delete_rule_groupsMixin0",
            query_params={
                "ids": ids,
                "comment": comment,
            },
            error_message="Failed to delete IOA rule groups",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def create_ioa_rule(
        self,
        rulegroup_id: str,  # was: Field()
        name: str,  # was: Field()
        ruletype_id: str,  # was: Field()
        disposition_id: int,  # was: Field()
        pattern_severity: str,  # was: Field()
        field_values: list,  # was: Field(); field_values: list[dict[str, Any]]
        description: str | None = None,  # was: Field(default=None)
        comment: str | None = None,  # was: Field(default=None)
    ) -> list[dict[str, Any]]:
        """Create a new Custom IOA behavioral detection rule within a rule group.

        Before creating a rule:
        1. Use `falcon_get_ioa_rule_types` to discover available rule types, their IDs,
           required fields, and valid disposition IDs.
        2. Use `falcon_search_ioa_rule_groups` to find the target rule group ID.

        The `field_values` parameter defines the behavioral criteria the rule will match
        against (e.g., process names, file paths, command line patterns using regex).

        Args:
            rulegroup_id: ID of the rule group to add the rule to.
            name: Name for the new rule.
                Examples: {"Block cmd.exe spawned from Office", "Detect encoded PowerShell"}
            ruletype_id: Rule type ID that defines the detection category. Use `falcon_get_ioa_rule_types` to find valid IDs.
            disposition_id: Disposition ID that determines the action taken when the rule fires. Use `falcon_get_ioa_rule_types` to find valid disposition IDs for the rule type.
            pattern_severity: Severity level for this rule. Allowed values: critical, high, medium, low, informational.
                Examples: {"critical", "high", "medium", "low", "informational"}
            field_values: List of field value objects that define the rule's matching criteria. Each field value object should include: 'name' (field name), 'value' (match value), and optionally 'label', 'type', 'final_value', 'values' (list of label/value pairs). Use `falcon_get_ioa_rule_types` to discover required fields for the chosen rule type.
                Examples: { '[{"name": "GrandparentImageFilename", "value": ".*\\\\\\\\\\\\\\\\winword\\\\\\\\.exe", "label": "Grand Parent Image Filename"}]' }
            description: Optional description for the rule.
            comment: Audit comment explaining why this rule is being created.
        """
        body: dict[str, Any] = {
            "rulegroup_id": rulegroup_id,
            "name": name,
            "ruletype_id": ruletype_id,
            "disposition_id": disposition_id,
            "pattern_severity": pattern_severity,
            "field_values": field_values,
        }
        if description is not None:
            body["description"] = description
        if comment is not None:
            body["comment"] = comment

        result = self._base_query_api_call(
            operation="create_rule",
            body_params=body,
            error_message="Failed to create IOA rule",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def update_ioa_rule(
        self,
        rulegroup_id: str,  # was: Field()
        rulegroup_version: int,  # was: Field()
        instance_id: str,  # was: Field()
        name: str | None = None,  # was: Field(default=None)
        description: str | None = None,  # was: Field(default=None)
        enabled: bool = None,  # was: Field(default=None); enabled: bool | None
        pattern_severity: str | None = None,  # was: Field(default=None)
        disposition_id: int = None,  # was: Field(default=None); disposition_id: int | None
        field_values: list = None,  # was: Field(default=None); field_values: list[dict[str, Any]] | None
        comment: str | None = None,  # was: Field(default=None)
    ) -> list[dict[str, Any]]:
        """Update an existing Custom IOA behavioral detection rule.

        The `rulegroup_version` is required for optimistic locking to prevent
        concurrent modification conflicts. Use `falcon_search_ioa_rule_groups` to
        retrieve the current version and instance ID.

        Args:
            rulegroup_id: ID of the rule group containing the rule.
            rulegroup_version: Current version of the rule group. Required for optimistic locking. Retrieve from `falcon_search_ioa_rule_groups`.
            instance_id: Instance ID of the rule to update. Retrieve from `falcon_search_ioa_rule_groups`.
            name: New name for the rule.
            description: New description for the rule.
            enabled: Whether the rule should be enabled or disabled.
            pattern_severity: New severity level. Allowed values: critical, high, medium, low, informational.
            disposition_id: New disposition ID for the action taken when the rule fires.
            field_values: Updated field value objects that define the rule's matching criteria.
            comment: Audit comment explaining why the rule is being updated.
        """
        rule_update: dict[str, Any] = {
            "instance_id": instance_id,
            "rulegroup_version": rulegroup_version,
        }
        if name is not None:
            rule_update["name"] = name
        if description is not None:
            rule_update["description"] = description
        if enabled is not None:
            rule_update["enabled"] = enabled
        if pattern_severity is not None:
            rule_update["pattern_severity"] = pattern_severity
        if disposition_id is not None:
            rule_update["disposition_id"] = disposition_id
        if field_values is not None:
            rule_update["field_values"] = field_values

        body: dict[str, Any] = {
            "rulegroup_id": rulegroup_id,
            "rulegroup_version": rulegroup_version,
            "rule_updates": [rule_update],
        }
        if comment is not None:
            body["comment"] = comment

        result = self._base_query_api_call(
            operation="update_rules_v2",
            body_params=body,
            error_message="Failed to update IOA rule",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def delete_ioa_rules(
        self,
        rule_group_id: str,  # was: Field()
        ids: list,  # was: Field(); ids: list[str]
        comment: str | None = None,  # was: Field(default=None)
    ) -> list[dict[str, Any]]:
        """Delete Custom IOA behavioral detection rules from a rule group.

        Use `falcon_search_ioa_rule_groups` to find the rule group ID and
        the individual rule IDs (instance IDs) to delete.

        Args:
            rule_group_id: ID of the rule group containing the rules to delete.
            ids: IDs of the rules to delete. Retrieve from `falcon_search_ioa_rule_groups`.
            comment: Audit comment explaining why the rules are being deleted.
        """
        if not ids:
            return [
                _format_error_response(
                    "`ids` must be provided to delete IOA rules.",
                    operation="delete_rules",
                )
            ]

        result = self._base_query_api_call(
            operation="delete_rules",
            query_params={
                "rule_group_id": rule_group_id,
                "ids": ids,
                "comment": comment,
            },
            error_message="Failed to delete IOA rules",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result
