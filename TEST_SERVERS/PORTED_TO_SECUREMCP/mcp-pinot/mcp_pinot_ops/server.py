"""
mcp_pinot_ops server (SecureMCP port).

WHAT THIS FILE USED TO DO
=========================
The original mcp_pinot_ops server used the low-level MCP Server pattern:

  - One @server.list_prompts / @server.get_prompt pair that
    advertised a single "pinot-query" prompt.
  - One @server.list_tools that returned 21 hand-built Tool() objects
    with literal inputSchema dicts.
  - One @server.call_tool with a 21-branch if/elif dispatcher that
    forwarded to pinot_instance methods.
  - An async main() that wired stdio_server() + server.run() with
    explicit InitializationOptions and capabilities.

WHAT THIS FILE DOES NOW
=======================
Same 21 tools, plus the prompt, but each is a normal SecureMCP
decorator at module level. Each wrapper:

  - has typed Python kwargs matching the original inputSchema
  - calls the same pinot_instance.<method>(...) the dispatcher used
  - returns str(result) to match the original handler's
    `text=str(results)` shape

The original tool NAMES are preserved verbatim via @app.tool(name=...)
because they use hyphens (e.g., "list-tables") which can't appear in
Python function names. Function names use underscores; the public
mesh-advertised name is the original.

The transport machinery (stdio_server + InitializationOptions +
capabilities) is dropped -- SecureMCP's app.run() carries traffic via
the MACAW mesh.

The original code is preserved as comment blocks below for review.
See MIGRATION.txt for the full port plan.
"""

import logging
from typing import Any, List, Optional

# import asyncio                                          # PORT: not needed; SecureMCP owns asyncio.run()
# import sys                                              # PORT: only used by the dropped error-printing in original main()
# from mcp.server import NotificationOptions, Server      # PORT
# from mcp.server.models import InitializationOptions     # PORT
# import mcp.server.stdio                                 # PORT
# import mcp.types as types                               # PORT
from macaw_adapters.mcp import SecureMCP

from mcp_pinot_ops.prompts import PROMPT_TEMPLATE
from mcp_pinot_ops.utils.pinot_client import Pinot

logger = logging.getLogger("pinot_mcp_table_ops_claude")
logger.setLevel(logging.INFO)

# Use the imported Pinot class and connection values
# (Module-level singleton: same semantic as the original.)
pinot_instance = Pinot()

# PORT: was `server = Server(...)` inside async main(). Move it to module
# level so @app.tool decorators fire at import time -- the standard
# SecureMCP pattern.
app = SecureMCP("pinot_mcp_table_ops_claude")


# ======================================================================
# PORT NOTE -- Prompt
# ----------------------------------------------------------------------
# Original had @server.list_prompts (returning one Prompt named
# "pinot-query") AND @server.get_prompt (returning the PROMPT_TEMPLATE
# wrapped in a GetPromptResult). Under SecureMCP, @app.prompt() is the
# single decorator -- it registers the prompt and provides the content.
# Tool name is preserved.
# ======================================================================
# @server.list_prompts()
# async def handle_list_prompts() -> list[types.Prompt]:
#     return [
#         types.Prompt(
#             name="pinot-query",
#             description="A prompt to query the Pinot database with a Pinot MCP Server + Claude",
#             arguments=[],
#         )
#     ]
#
# @server.get_prompt()
# async def handle_get_prompt(name, arguments):
#     if name != "pinot-query":
#         raise ValueError(f"Unknown prompt: {name}")
#     return types.GetPromptResult(
#         description="Pinot query assistance template",
#         messages=[
#             types.PromptMessage(
#                 role="user",
#                 content=types.TextContent(type="text", text=PROMPT_TEMPLATE.strip()),
#             )
#         ],
#     )


@app.prompt(
    name="pinot-query",
    description="A prompt to query the Pinot database with a Pinot MCP Server + Claude",
)
def pinot_query_prompt() -> str:
    """Return the Pinot query assistance template."""
    return PROMPT_TEMPLATE.strip()


# ======================================================================
# PORT NOTE -- 21 tools
# ----------------------------------------------------------------------
# The original had @server.list_tools (returning 21 Tool objects with
# literal inputSchema dicts) and @server.call_tool (a 21-branch if/elif
# dispatcher). Under SecureMCP, each tool becomes one @app.tool function
# whose typed kwargs ARE the schema. The function bodies are the
# original dispatcher branches inlined, so pinot_instance is called
# with the same kwargs the original arguments dict supplied.
#
# Public tool names (advertised on the mesh) preserved verbatim via
# @app.tool(name=...). Function names use underscores because Python
# identifiers can't include hyphens.
#
# Errors: original wrapped the WHOLE dispatcher in try/except and
# returned `text=f"Error: {str(e)}"`. Each wrapper here mirrors that
# behaviour individually, returning the error as a plain string so
# mesh callers see a consistent surface.
#
# Original @server.list_tools and @server.call_tool blocks are
# preserved as a single comment block at the bottom of this file.
# ======================================================================


def _err(e: Exception) -> str:
    """Format an exception the same way the original dispatcher did."""
    return f"Error: {str(e)}"


# Tool 1: list-tables
@app.tool(name="list-tables", description="List all tables in Pinot")
def list_tables() -> str:
    """List all tables in Pinot."""
    try:
        return str(pinot_instance._get_tables())
    except Exception as e:
        return _err(e)


# Tool 2: table-details
@app.tool(name="table-details", description="Get table size details")
def table_details(tableName: str) -> str:
    """Get table size details.

    Args:
        tableName: Table name.
    """
    try:
        return str(pinot_instance._get_table_detail(tableName=tableName))
    except Exception as e:
        return _err(e)


# Tool 3: segment-list
@app.tool(name="segment-list", description="List segments for a table")
def segment_list(tableName: str) -> str:
    """List segments for a table.

    Args:
        tableName: Table name.
    """
    try:
        return str(pinot_instance._get_segments(tableName=tableName))
    except Exception as e:
        return _err(e)


# Tool 4: index-column-details
@app.tool(
    name="index-column-details",
    description="Get index/column details for a segment",
)
def index_column_details(tableName: str, segmentName: str) -> str:
    """Get index/column details for a segment.

    Args:
        tableName: Table name.
        segmentName: Segment name.
    """
    try:
        return str(
            pinot_instance._get_index_column_detail(
                tableName=tableName, segmentName=segmentName
            )
        )
    except Exception as e:
        return _err(e)


# Tool 5: segment-metadata-details
@app.tool(
    name="segment-metadata-details",
    description="Get metadata for segments of a table",
)
def segment_metadata_details(tableName: str) -> str:
    """Get metadata for segments of a table.

    Args:
        tableName: Table name.
    """
    try:
        return str(pinot_instance._get_segment_metadata_detail(tableName=tableName))
    except Exception as e:
        return _err(e)


# Tool 6: tableconfig-schema-details
@app.tool(
    name="tableconfig-schema-details",
    description="Get table config and schema",
)
def tableconfig_schema_details(tableName: str) -> str:
    """Get table config and schema.

    Args:
        tableName: Table name.
    """
    try:
        return str(pinot_instance._get_tableconfig_schema_detail(tableName=tableName))
    except Exception as e:
        return _err(e)


# Tool 7: pause_consumption
@app.tool(
    name="pause_consumption",
    description="Pause consumption of a realtime table",
)
def pause_consumption(tableName: str, comment: Optional[str] = None) -> str:
    """Pause consumption of a realtime table.

    Args:
        tableName: Name of the table.
        comment: Optional comment.
    """
    try:
        return str(
            pinot_instance._pause_consumption(tableName=tableName, comment=comment)
        )
    except Exception as e:
        return _err(e)


# Tool 8: resume_consumption
@app.tool(
    name="resume_consumption",
    description="Resume consumption of a realtime table",
)
def resume_consumption(
    tableName: str,
    comment: Optional[str] = None,
    consumeFrom: Optional[str] = None,
) -> str:
    """Resume consumption of a realtime table.

    Args:
        tableName: Name of the table.
        comment: Optional comment.
        consumeFrom: One of "lastConsumed", "smallest", or "largest".
    """
    try:
        return str(
            pinot_instance._resume_consumption(
                tableName=tableName, comment=comment, consumeFrom=consumeFrom
            )
        )
    except Exception as e:
        return _err(e)


# Tool 9: force_commit
@app.tool(
    name="force_commit",
    description="Force commit the current consuming segments",
)
def force_commit(
    tableName: str,
    partitions: Optional[str] = None,
    segments: Optional[str] = None,
    batchSize: Optional[int] = None,
    batchStatusCheckIntervalSec: Optional[int] = None,
    batchStatusCheckTimeoutSec: Optional[int] = None,
) -> str:
    """Force commit the current consuming segments.

    Args:
        tableName: Name of the table.
        partitions: Comma-separated partition group IDs.
        segments: Comma-separated consuming segments.
        batchSize: Max segments to commit at once.
        batchStatusCheckIntervalSec: Interval to check batch status.
        batchStatusCheckTimeoutSec: Timeout for batch status check.
    """
    try:
        return str(
            pinot_instance._force_commit(
                tableName=tableName,
                partitions=partitions,
                segments=segments,
                batchSize=batchSize,
                batchStatusCheckIntervalSec=batchStatusCheckIntervalSec,
                batchStatusCheckTimeoutSec=batchStatusCheckTimeoutSec,
            )
        )
    except Exception as e:
        return _err(e)


# Tool 10: get_pause_status
@app.tool(
    name="get_pause_status",
    description="Return pause status of a realtime table",
)
def get_pause_status(tableName: str) -> str:
    """Return pause status of a realtime table.

    Args:
        tableName: Name of the table.
    """
    try:
        return str(pinot_instance._get_pause_status(tableName=tableName))
    except Exception as e:
        return _err(e)


# Tool 11: get_consuming_segments_info
@app.tool(
    name="get_consuming_segments_info",
    description=(
        "Gets the status of consumers from all servers for a realtime table"
    ),
)
def get_consuming_segments_info(tableName: str) -> str:
    """Get the status of consumers from all servers for a realtime table.

    Args:
        tableName: Realtime table name with or without type.
    """
    try:
        return str(pinot_instance._get_consuming_segments_info(tableName=tableName))
    except Exception as e:
        return _err(e)


# Tool 12: reload-table-segments
# Note: original kwarg is named `type` -- we keep it that way to preserve
# the public schema name (clients pass {"type": "REALTIME"}). It shadows
# the Python built-in inside the function but that's harmless.
@app.tool(
    name="reload-table-segments",
    description=(
        "Reload all segments for a table (applies config changes, can "
        "force download)"
    ),
)
def reload_table_segments(
    tableName: str,
    type: Optional[str] = None,
    forceDownload: bool = False,
) -> str:
    """Reload all segments for a table.

    Args:
        tableName: Name of the table.
        type: "OFFLINE" or "REALTIME".
        forceDownload: Whether to force servers to re-download segments.
    """
    try:
        return str(
            pinot_instance._reload_table_segments(
                tableName=tableName,
                tableType=type,  # API uses 'type' query param
                forceDownload=forceDownload,
            )
        )
    except Exception as e:
        return _err(e)


# Tool 13: rebalance-table
# Same `type` kwarg note as above -- required here.
@app.tool(
    name="rebalance-table",
    description="Rebalances a table (reassign instances and segments)",
)
def rebalance_table(
    tableName: str,
    type: str,
    dryRun: bool = False,
    reassignInstances: bool = True,
    includeConsuming: bool = True,
    bootstrap: bool = False,
    downtime: bool = False,
    minAvailableReplicas: int = -1,
) -> str:
    """Rebalance a table.

    Args:
        tableName: Name of the table to rebalance.
        type: "OFFLINE" or "REALTIME".
        dryRun: Dry run mode.
        reassignInstances: Reassign instances before segments.
        includeConsuming: Reassign CONSUMING segments (REALTIME only).
        bootstrap: Bootstrap mode (ignore minimal data movement).
        downtime: Allow downtime.
        minAvailableReplicas: Min replicas during no-downtime rebalance.
    """
    try:
        return str(
            pinot_instance._rebalance_table(
                tableName=tableName,
                tableType=type,
                dryRun=dryRun,
                reassignInstances=reassignInstances,
                includeConsuming=includeConsuming,
                bootstrap=bootstrap,
                downtime=downtime,
                minAvailableReplicas=minAvailableReplicas,
            )
        )
    except Exception as e:
        return _err(e)


# Tool 14: reset-table-segments
@app.tool(
    name="reset-table-segments",
    description=(
        "Resets segments for a table (disable->wait->enable). Use "
        "tableNameWithType (e.g., myTable_REALTIME)"
    ),
)
def reset_table_segments(
    tableNameWithType: str,
    errorSegmentsOnly: bool = False,
) -> str:
    """Reset segments for a table.

    Args:
        tableNameWithType: Table name with type suffix (e.g., myTable_REALTIME).
        errorSegmentsOnly: Reset only segments in ERROR state.
    """
    try:
        return str(
            pinot_instance._reset_table_segments(
                tableNameWithType=tableNameWithType,
                errorSegmentsOnly=errorSegmentsOnly,
            )
        )
    except Exception as e:
        return _err(e)


# Tool 15: list-supported-indices
@app.tool(
    name="list-supported-indices",
    description="List the types of indices supported by Pinot",
)
def list_supported_indices() -> str:
    """List the types of indices supported by Pinot.

    Returns a static newline-separated list -- no Pinot call.
    """
    supported_indices = [
        (
            "Forward Index (Dictionary-encoded, Sorted, Raw Value) - "
            "Default, based on encoding/sorting"
        ),
        "Inverted Index (Bitmap, Sorted) - For exact match filtering",
        "Range Index - For range filtering (<, >, <=, >=)",
        "Text Index (Native/Lucene) - For text search queries",
        "JSON Index - For filtering fields within JSON blobs",
        (
            "Geospatial Index (H3) - For geospatial "
            "distance/containment queries"
        ),
        "Timestamp Index - Optimized time filtering",
        "Vector Index - For vector similarity search",
        "Bloom Filter - Probabilistic filter to skip segments",
        "Star-Tree Index - Pre-aggregation cube.",
        (
            "FST Index - For prefix/regex matching on "
            "dictionary-encoded columns"
        ),
    ]
    return "\n".join(supported_indices)


# Tool 16: create-schema
@app.tool(name="create-schema", description="Adds a new schema to Pinot")
def create_schema(
    schemaJson: str,
    override: bool = True,
    force: bool = False,
) -> str:
    """Add a new schema to Pinot.

    Args:
        schemaJson: The schema definition in JSON format.
        override: Override if schema exists.
        force: Force override even if incompatible.
    """
    try:
        return str(
            pinot_instance._create_schema(
                schemaJson=schemaJson, override=override, force=force
            )
        )
    except Exception as e:
        return _err(e)


# Tool 17: update-schema
@app.tool(name="update-schema", description="Updates an existing schema in Pinot")
def update_schema(
    schemaName: str,
    schemaJson: str,
    reload: bool = False,
    force: bool = False,
) -> str:
    """Update an existing schema in Pinot.

    Args:
        schemaName: Name of the schema to update.
        schemaJson: The updated schema definition in JSON format.
        reload: Reload table after update.
        force: Force update even if incompatible.
    """
    try:
        return str(
            pinot_instance._update_schema(
                schemaName=schemaName,
                schemaJson=schemaJson,
                reload=reload,
                force=force,
            )
        )
    except Exception as e:
        return _err(e)


# Tool 18: create-table-config
@app.tool(
    name="create-table-config",
    description="Adds a new table configuration to Pinot",
)
def create_table_config(
    tableConfigJson: str,
    validationTypesToSkip: Optional[str] = None,
) -> str:
    """Add a new table configuration to Pinot.

    Args:
        tableConfigJson: The table configuration in JSON format.
        validationTypesToSkip: Comma-separated validation types to skip
                               (ALL|TASK|UPSERT).
    """
    try:
        return str(
            pinot_instance._create_table_config(
                tableConfigJson=tableConfigJson,
                validationTypesToSkip=validationTypesToSkip,
            )
        )
    except Exception as e:
        return _err(e)


# Tool 19: update-table-config
@app.tool(
    name="update-table-config",
    description=(
        "Updates an existing table configuration in Pinot (can be used "
        "to add/modify indices)"
    ),
)
def update_table_config(
    tableName: str,
    tableConfigJson: str,
    validationTypesToSkip: Optional[str] = None,
) -> str:
    """Update an existing table configuration in Pinot.

    Args:
        tableName: Name of the table to update.
        tableConfigJson: The updated table configuration in JSON format.
        validationTypesToSkip: Comma-separated validation types to skip
                               (ALL|TASK|UPSERT).
    """
    try:
        return str(
            pinot_instance._update_table_config(
                tableName=tableName,
                tableConfigJson=tableConfigJson,
                validationTypesToSkip=validationTypesToSkip,
            )
        )
    except Exception as e:
        return _err(e)


# Tool 20: add-index
@app.tool(
    name="add-index",
    description=(
        "Adds a specified index type to one or more columns in a table "
        "config and optionally reloads"
    ),
)
def add_index(
    tableName: str,
    indexType: str,
    columns: List[str],
    tableType: Optional[str] = None,
    triggerReload: bool = True,
) -> str:
    """Add a specified index type to one or more columns.

    Args:
        tableName: Name of the table (without type suffix).
        indexType: Type of index ("inverted", "range", "text", "json",
                   "bloom", "fst", "sorted").
        columns: List of column names to add the index to.
        tableType: "OFFLINE" or "REALTIME" (required if table has both
                   types).
        triggerReload: Reload the table segments after updating config.
    """
    try:
        return str(
            pinot_instance._add_index(
                tableName=tableName,
                tableType=tableType,
                indexType=indexType,
                columns=columns,
                triggerReload=triggerReload,
            )
        )
    except Exception as e:
        return _err(e)


# Tool 21: add-startree-index
@app.tool(
    name="add-startree-index",
    description=(
        "Adds a Star-Tree index configuration to a table config and "
        "optionally reloads."
    ),
)
def add_startree_index(
    tableName: str,
    dimensionsSplitOrder: List[str],
    tableType: Optional[str] = None,
    functionColumnPairs: Optional[List[str]] = None,
    aggregationConfigsJson: Optional[str] = None,
    skipStarNodeCreationForDimensions: Optional[List[str]] = None,
    maxLeafRecords: int = 10000,
    triggerReload: bool = True,
) -> str:
    """Add a Star-Tree index configuration to a table config.

    Args:
        tableName: Name of the table (without type suffix).
        dimensionsSplitOrder: List of dimension columns defining the
                              tree structure.
        tableType: "OFFLINE" or "REALTIME" (required if table has both
                   types).
        functionColumnPairs: Optional. Aggregations like
                             ["SUM__colA", "COUNT__*"]. Use this OR
                             aggregationConfigsJson.
        aggregationConfigsJson: Optional. JSON string for the
                                'aggregationConfigs' array (alternative
                                to functionColumnPairs).
        skipStarNodeCreationForDimensions: Optional. Dimensions to skip
                                           Star-node creation for.
        maxLeafRecords: Threshold T for splitting nodes (default 10000).
        triggerReload: Reload the table segments after updating config.
    """
    try:
        # Preserve the original validation: only one of
        # functionColumnPairs / aggregationConfigsJson may be set.
        if functionColumnPairs and aggregationConfigsJson:
            raise ValueError(
                "Provide either 'functionColumnPairs' or "
                "'aggregationConfigsJson', not both."
            )

        return str(
            pinot_instance._add_star_tree_index(
                tableName=tableName,
                tableType=tableType,
                dimensionsSplitOrder=dimensionsSplitOrder,
                functionColumnPairs=functionColumnPairs or [],
                aggregationConfigsJson=aggregationConfigsJson,
                skipStarNodeCreationForDimensions=(
                    skipStarNodeCreationForDimensions or []
                ),
                maxLeafRecords=maxLeafRecords,
                triggerReload=triggerReload,
            )
        )
    except Exception as e:
        return _err(e)


# ======================================================================
# PORT NOTE -- entry point
# ----------------------------------------------------------------------
# Original async main() did:
#   - server = Server("pinot_mcp_table_ops_claude")
#   - registered the prompt + tool decorators inline
#   - async with stdio_server() as (read, write):
#       await server.run(read, write, InitializationOptions(...))
#   - try/except around the whole thing for traceback printing
#
# Under SecureMCP `app.run()` is sync, creates its own asyncio.run()
# internally (mcp.py:628-635), and registers the server as a mesh
# agent. No stdio plumbing, no InitializationOptions, no capabilities
# negotiation -- those are MCP-protocol-layer concerns the mesh
# replaces.
#
# Original code preserved as a comment block below.
# ======================================================================
# async def main():
#     logger.info("Starting Pinot MCP Table Ops Server")
#     server = Server("pinot_mcp_table_ops_claude")
#     # ... 31 lines of @server.list_prompts / @server.get_prompt
#     # ... 515 lines of @server.list_tools returning 21 Tool() objects
#     # ... 208 lines of @server.call_tool with a 21-branch if/elif
#     try:
#         async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
#             logger.info("Server running with stdio transport")
#             await server.run(
#                 read_stream,
#                 write_stream,
#                 InitializationOptions(
#                     server_name="pinot_mcp_table_ops_claude",
#                     server_version="0.1.0",
#                     capabilities=server.get_capabilities(
#                         notification_options=NotificationOptions(),
#                         experimental_capabilities={},
#                     ),
#                 ),
#             )
#     except Exception as e:
#         import traceback
#         logger.error(f"Error running MCP server: {e}")
#         logger.error(traceback.format_exc())
#         print(f"Error running MCP server: {e}", file=sys.stderr)
#         print(traceback.format_exc(), file=sys.stderr)
#         raise
#
#
# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())


def main():
    """Run the SecureMCP server (sync; SecureMCP owns its asyncio.run())."""
    logger.info("Starting Pinot MCP Table Ops Server on the MACAW mesh")
    app.run()


if __name__ == "__main__":
    main()
