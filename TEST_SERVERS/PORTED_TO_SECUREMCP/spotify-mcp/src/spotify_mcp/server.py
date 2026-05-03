"""
spotify-mcp server (SecureMCP port).

PORT NOTE -- FastMCP/low-level Server -> SecureMCP
==================================================
The original used the low-level mcp.server.Server with a static
@server.list_tools() returning Pydantic-derived Tool objects, plus a
@server.call_tool() generic dispatcher that branched on tool name.
That is the "old format" PORT-shape per the skill (Step 0 row 3):
the tool list is static, defined entirely in source, and each tool
has a discrete code path. Collapse to modern @mcp.tool() decorators.

Per the skill, original code is preserved as comment blocks below;
do not delete it. Reviewers should be able to see exactly what was
removed and why.
"""

# import asyncio                                            
import base64
import os
import logging
import sys
from enum import Enum
import json
from typing import List, Optional, Tuple
from datetime import datetime
from pathlib import Path

# PORT: low-level MCP imports replaced by SecureMCP. Kept commented for review.
# import mcp.types as types
# from mcp.server import NotificationOptions, Server  # , stdio_server
# import mcp.server.stdio
from macaw_adapters.mcp import SecureMCP

from pydantic import BaseModel, Field, AnyUrl
from spotipy import SpotifyException

from . import spotify_api
from .utils import normalize_redirect_uri


def setup_logger():
    class Logger:
        def info(self, message):
            print(f"[INFO] {message}", file=sys.stderr)

        def error(self, message):
            print(f"[ERROR] {message}", file=sys.stderr)

    return Logger()


logger = setup_logger()
# Normalize the redirect URI to meet Spotify's requirements
if spotify_api.REDIRECT_URI:
    spotify_api.REDIRECT_URI = normalize_redirect_uri(spotify_api.REDIRECT_URI)
spotify_client = spotify_api.Client(logger)

# PORT: was: server = Server("spotify-mcp")
mcp = SecureMCP("spotify-mcp")


# ======================================================================
# PORT: ToolModel + 5 subclasses kept commented for reference. SecureMCP
# derives schemas from each @mcp.tool function's signature; these
# Pydantic models are no longer wired. Per-field Field(description=...)
# hints have moved to each tool's docstring Args: section because
# SecureMCP's _extract_parameters does not read pydantic.Field metadata
# (mcp.py:827-859 -- 6-entry type table only).
# ======================================================================
# class ToolModel(BaseModel):
#     @classmethod
#     def as_tool(cls):
#         return types.Tool(
#             name="Spotify" + cls.__name__,
#             description=cls.__doc__,
#             inputSchema=cls.model_json_schema()
#         )
#
#
# class Playback(ToolModel):
#     """Manages the current playback with the following actions:
#     - get: Get information about user's current track.
#     - start: Starts playing new item or resumes current playback if called with no uri.
#     - pause: Pauses current playback.
#     - skip: Skips current track.
#     """
#     action: str = Field(description="Action to perform: 'get', 'start', 'pause' or 'skip'.")
#     spotify_uri: Optional[str] = Field(default=None, description="Spotify uri of item to play for 'start' action. " +
#                                                                  "If omitted, resumes current playback.")
#     num_skips: Optional[int] = Field(default=1, description="Number of tracks to skip for `skip` action.")
#
#
# class Queue(ToolModel):
#     """Manage the playback queue - get the queue or add tracks."""
#     action: str = Field(description="Action to perform: 'add' or 'get'.")
#     track_id: Optional[str] = Field(default=None, description="Track ID to add to queue (required for add action)")
#
#
# class GetInfo(ToolModel):
#     """Get detailed information about a Spotify item (track, album, artist, or playlist)."""
#     item_uri: str = Field(description="URI of the item to get information about. " +
#                                       "If 'playlist' or 'album', returns its tracks. " +
#                                       "If 'artist', returns albums and top tracks.")
#
#
# class Search(ToolModel):
#     """Search for tracks, albums, artists, or playlists on Spotify."""
#     query: str = Field(description="query term")
#     qtype: Optional[str] = Field(default="track",
#                                  description="Type of items to search for (track, album, artist, playlist, " +
#                                              "or comma-separated combination)")
#     limit: Optional[int] = Field(default=10, description="Maximum number of items to return")
#
#
# class Playlist(ToolModel):
#     """Manage Spotify playlists.
#     - get: Get a list of user's playlists.
#     - get_tracks: Get tracks in a specific playlist.
#     - add_tracks: Add tracks to a specific playlist.
#     - remove_tracks: Remove tracks from a specific playlist.
#     - change_details: Change details of a specific playlist.
#     - create: Create a new playlist.
#     """
#     action: str = Field(
#         description="Action to perform: 'get', 'get_tracks', 'add_tracks', 'remove_tracks', 'change_details', 'create'.")
#     playlist_id: Optional[str] = Field(default=None, description="ID of the playlist to manage.")
#     track_ids: Optional[List[str]] = Field(default=None, description="List of track IDs to add/remove.")
#     name: Optional[str] = Field(default=None, description="Name for the playlist (required for create and change_details).")
#     description: Optional[str] = Field(default=None, description="Description for the playlist.")
#     public: Optional[bool] = Field(default=True, description="Whether the playlist should be public (for create action).")


# ======================================================================
# PORT: removed @server.list_prompts / list_resources / list_tools /
# call_tool. Both list_prompts and list_resources returned []
# (no prompts/resources exposed). list_tools and call_tool are
# replaced by the 5 @mcp.tool() functions below.
# ======================================================================
# @server.list_prompts()
# async def handle_list_prompts() -> list[types.Prompt]:
#     return []
#
#
# @server.list_resources()
# async def handle_list_resources() -> list[types.Resource]:
#     return []
#
#
# @server.list_tools()
# async def handle_list_tools() -> list[types.Tool]:
#     """List available tools."""
#     logger.info("Listing available tools")
#     tools = [
#         Playback.as_tool(),
#         Search.as_tool(),
#         Queue.as_tool(),
#         GetInfo.as_tool(),
#         Playlist.as_tool(),
#     ]
#     logger.info(f"Available tools: {[tool.name for tool in tools]}")
#     return tools
#
#
# @server.call_tool()
# async def handle_call_tool(
#         name: str, arguments: dict | None
# ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
#     # Original generic dispatcher with `match name[7:]:` branching on
#     # tool name -- ~230 lines. Replaced by per-tool @mcp.tool functions
#     # below. See git history for the full original body.


# ======================================================================
# PORT: 5 modern @mcp.tool() functions replacing the low-level
# list_tools / call_tool dispatcher. Each preserves the original tool
# name (Spotify-prefixed) and multi-action semantics. Function bodies
# call the unchanged spotify_client (sync SDK -- spotipy).
# ======================================================================


@mcp.tool(
    name="SpotifyPlayback",
    description=(
        "Manages the current playback with the following actions:\n"
        "- get: Get information about user's current track.\n"
        "- start: Starts playing new item or resumes current playback if called with no uri.\n"
        "- pause: Pauses current playback.\n"
        "- skip: Skips current track."
    ),
)
async def SpotifyPlayback(
    action: str,
    spotify_uri: Optional[str] = None,
    num_skips: Optional[int] = 1,
) -> dict:
    """Manage current playback.

    Args:
        action: Action to perform -- 'get', 'start', 'pause', or 'skip'.
        spotify_uri: Spotify URI of item to play for 'start' action. If omitted, resumes current playback.
        num_skips: Number of tracks to skip for 'skip' action.
    """
    try:
        logger.info(f"Playback called: action={action}, uri={spotify_uri}, num_skips={num_skips}")
        if action == "get":
            curr_track = spotify_client.get_current_track()
            if curr_track:
                logger.info(f"Current track retrieved: {curr_track.get('name', 'Unknown')}")
                return {"track": curr_track}
            return {"message": "No track playing."}
        elif action == "start":
            spotify_client.start_playback(spotify_uri=spotify_uri)
            return {"message": "Playback starting."}
        elif action == "pause":
            spotify_client.pause_playback()
            return {"message": "Playback paused."}
        elif action == "skip":
            spotify_client.skip_track(n=int(num_skips or 1))
            return {"message": "Skipped to next track."}
        else:
            return {"error": f"Unknown action: {action}"}
    except SpotifyException as se:
        logger.error(f"Spotify Client error: {se}")
        return {"error": f"An error occurred with the Spotify Client: {se}"}


@mcp.tool(
    name="SpotifySearch",
    description="Search for tracks, albums, artists, or playlists on Spotify.",
)
async def SpotifySearch(
    query: str,
    qtype: Optional[str] = "track",
    limit: Optional[int] = 10,
) -> dict:
    """Search Spotify.

    Args:
        query: Query term.
        qtype: Type of items to search for (track, album, artist, playlist, or comma-separated combination).
        limit: Maximum number of items to return.
    """
    try:
        logger.info(f"Search called: query={query!r}, qtype={qtype}, limit={limit}")
        results = spotify_client.search(query=query, qtype=qtype, limit=limit)
        return {"results": results}
    except SpotifyException as se:
        logger.error(f"Spotify Client error: {se}")
        return {"error": f"An error occurred with the Spotify Client: {se}"}


@mcp.tool(
    name="SpotifyQueue",
    description="Manage the playback queue - get the queue or add tracks.",
)
async def SpotifyQueue(
    action: str,
    track_id: Optional[str] = None,
) -> dict:
    """Manage the playback queue.

    Args:
        action: Action to perform -- 'add' or 'get'.
        track_id: Track ID to add to queue (required for 'add' action).
    """
    try:
        logger.info(f"Queue called: action={action}, track_id={track_id}")
        if action == "add":
            if not track_id:
                return {"error": "track_id is required for add action"}
            spotify_client.add_to_queue(track_id)
            return {"message": "Track added to queue."}
        elif action == "get":
            queue = spotify_client.get_queue()
            return {"queue": queue}
        else:
            return {"error": f"Unknown queue action: {action}. Supported actions are: add, get."}
    except SpotifyException as se:
        logger.error(f"Spotify Client error: {se}")
        return {"error": f"An error occurred with the Spotify Client: {se}"}


@mcp.tool(
    name="SpotifyGetInfo",
    description="Get detailed information about a Spotify item (track, album, artist, or playlist).",
)
async def SpotifyGetInfo(
    item_uri: str,
) -> dict:
    """Get info on a Spotify item.

    Args:
        item_uri: URI of the item to get information about. If 'playlist' or 'album', returns its tracks. If 'artist', returns albums and top tracks.
    """
    try:
        logger.info(f"GetInfo called: item_uri={item_uri}")
        info = spotify_client.get_info(item_uri=item_uri)
        return {"info": info}
    except SpotifyException as se:
        logger.error(f"Spotify Client error: {se}")
        return {"error": f"An error occurred with the Spotify Client: {se}"}


@mcp.tool(
    name="SpotifyPlaylist",
    description=(
        "Manage Spotify playlists.\n"
        "- get: Get a list of user's playlists.\n"
        "- get_tracks: Get tracks in a specific playlist.\n"
        "- add_tracks: Add tracks to a specific playlist.\n"
        "- remove_tracks: Remove tracks from a specific playlist.\n"
        "- change_details: Change details of a specific playlist.\n"
        "- create: Create a new playlist."
    ),
)
async def SpotifyPlaylist(
    action: str,
    playlist_id: Optional[str] = None,
    track_ids: Optional[List[str]] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    public: Optional[bool] = True,
) -> dict:
    """Manage playlists.

    Args:
        action: 'get', 'get_tracks', 'add_tracks', 'remove_tracks', 'change_details', or 'create'.
        playlist_id: ID of the playlist to manage.
        track_ids: List of track IDs to add/remove.
        name: Name for the playlist (required for 'create' and 'change_details').
        description: Description for the playlist.
        public: Whether the playlist should be public (for 'create' action).
    """
    try:
        logger.info(f"Playlist called: action={action}, playlist_id={playlist_id}")
        if action == "get":
            playlists = spotify_client.get_current_user_playlists()
            return {"playlists": playlists}
        elif action == "get_tracks":
            if not playlist_id:
                return {"error": "playlist_id is required for get_tracks action."}
            tracks = spotify_client.get_playlist_tracks(playlist_id)
            return {"tracks": tracks}
        elif action == "add_tracks":
            ids = track_ids
            if isinstance(ids, str):
                try:
                    ids = json.loads(ids)
                except json.JSONDecodeError:
                    return {"error": "track_ids must be a list or a valid JSON array."}
            spotify_client.add_tracks_to_playlist(playlist_id=playlist_id, track_ids=ids)
            return {"message": "Tracks added to playlist."}
        elif action == "remove_tracks":
            ids = track_ids
            if isinstance(ids, str):
                try:
                    ids = json.loads(ids)
                except json.JSONDecodeError:
                    return {"error": "track_ids must be a list or a valid JSON array."}
            spotify_client.remove_tracks_from_playlist(playlist_id=playlist_id, track_ids=ids)
            return {"message": "Tracks removed from playlist."}
        elif action == "change_details":
            if not playlist_id:
                return {"error": "playlist_id is required for change_details action."}
            if not name and not description:
                return {"error": "At least one of name, description, public, or collaborative is required."}
            spotify_client.change_playlist_details(
                playlist_id=playlist_id, name=name, description=description
            )
            return {"message": "Playlist details changed."}
        elif action == "create":
            if not name:
                return {"error": "name is required for create action."}
            playlist = spotify_client.create_playlist(
                name=name, description=description, public=public
            )
            return {"playlist": playlist}
        else:
            return {
                "error": (
                    f"Unknown playlist action: {action}. "
                    "Supported actions are: get, get_tracks, add_tracks, remove_tracks, change_details, create."
                )
            }
    except SpotifyException as se:
        logger.error(f"Spotify Client error: {se}")
        return {"error": f"An error occurred with the Spotify Client: {se}"}


# ======================================================================
# PORT: was async main() with stdio_server. SecureMCP.run() is sync
# (mcp.py:628-635: def run -> asyncio.run(_run_async)) and owns its
# own event loop internally; no stdio plumbing needed here.
# ======================================================================
# async def main():
#     try:
#         async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
#             await server.run(
#                 read_stream,
#                 write_stream,
#                 server.create_initialization_options()
#             )
#     except Exception as e:
#         logger.error(f"Server error occurred: {str(e)}")
#         raise


def main():
    """Run the SecureMCP server (sync; SecureMCP owns its asyncio.run() internally)."""
    try:
        mcp.run()
    except Exception as e:
        logger.error(f"Server error occurred: {str(e)}")
        raise
