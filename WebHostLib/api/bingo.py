"""
Bingo Tracker API Endpoints

Provides API endpoints for bingo board tracking:
- /api/bingo/<tracker_id> - Get bingo board with real-time completion status
- /api/bingo/<tracker_id>/upload - Upload a bingo board JSON
"""

import json
import os
from typing import Any, Dict, List, TypedDict
from uuid import UUID

from flask import abort, request, jsonify
from pony.orm import db_session

from WebHostLib import cache
from WebHostLib.api import api_endpoints
from WebHostLib.models import Room
from WebHostLib.tracker import TrackerData
from Utils import output_path


class BingoTile(TypedDict):
    """Represents a single bingo tile with completion status."""
    location: str
    player: int
    game: str
    sphere: int
    item: str
    location_id: int | None  # Resolved location ID
    completed: bool  # Whether this location has been checked


class BingoStatus(TypedDict):
    """Status of bingo board completion."""
    total_tiles: int
    completed_tiles: int
    completion_percentage: float
    completed_lines: List[str]  # e.g., ["row_0", "col_2", "diag_main"]


@api_endpoints.route("/bingo/<suuid:tracker>")
@cache.memoize(timeout=10)  # Cache for 10 seconds (faster updates than main tracker)
def bingo_tracker(tracker: UUID) -> Dict[str, Any]:
    """
    Get bingo board with real-time completion status.

    Returns:
        - board: 5x5 grid of tiles with completion status
        - status: Overall bingo completion statistics
        - seed: Seed name/number
        - difficulty: Bingo difficulty level
    """
    room: Room | None = Room.get(tracker=tracker)
    if not room:
        abort(404, description="Room not found")

    tracker_data = TrackerData(room)

    # Try to load bingo board from uploaded file or seed directory
    bingo_data = _load_bingo_board(tracker, tracker_data.get_seed_name())
    if not bingo_data:
        abort(404, description="No bingo board found for this tracker. Upload one first.")

    # Get all checked locations for all players
    all_players = tracker_data.get_all_players()
    checked_locations = {}
    location_name_maps = {}

    for team, players in all_players.items():
        for player in players:
            checked_locs = tracker_data.get_player_checked_locations(team, player)
            checked_locations[(team, player)] = checked_locs

            # Build location name -> ID mapping for this player
            game = tracker_data.get_player_game(player)
            if game not in location_name_maps:
                location_name_maps[game] = tracker_data.location_name_to_id.get(game, {})

    # Process board and mark completed tiles
    board_with_status = _process_bingo_board(
        bingo_data["board"],
        checked_locations,
        location_name_maps
    )

    # Calculate completion statistics
    status = _calculate_bingo_status(board_with_status)

    return {
        "board": board_with_status,
        "status": status,
        "seed": tracker_data.get_seed_name(),
        "difficulty": bingo_data.get("difficulty", "unknown"),
        "metadata": bingo_data.get("metadata", {}),
    }


@api_endpoints.route("/bingo/<suuid:tracker>/upload", methods=["POST"])
def bingo_upload(tracker: UUID) -> Dict[str, Any]:
    """
    Upload a bingo board JSON for a specific tracker session.

    Expects multipart/form-data with a 'bingo_file' field containing the JSON file.
    """
    room: Room | None = Room.get(tracker=tracker)
    if not room:
        abort(404, description="Room not found")

    if 'bingo_file' not in request.files:
        abort(400, description="No bingo_file provided")

    file = request.files['bingo_file']
    if file.filename == '':
        abort(400, description="No file selected")

    if not file.filename.endswith('.json'):
        abort(400, description="File must be a JSON file")

    try:
        bingo_data = json.load(file)

        # Validate bingo data structure
        if not _validate_bingo_data(bingo_data):
            abort(400, description="Invalid bingo board format")

        # Save to tracker-specific location
        _save_bingo_board(tracker, bingo_data)

        return jsonify({
            "success": True,
            "message": "Bingo board uploaded successfully",
            "seed": bingo_data.get("seed"),
            "difficulty": bingo_data.get("difficulty")
        })

    except json.JSONDecodeError:
        abort(400, description="Invalid JSON file")
    except Exception as e:
        abort(500, description=f"Error saving bingo board: {str(e)}")


@api_endpoints.route("/bingo/<suuid:tracker>/check")
def bingo_check_available(tracker: UUID) -> Dict[str, Any]:
    """
    Check if a bingo board is available for this tracker.
    """
    room: Room | None = Room.get(tracker=tracker)
    if not room:
        abort(404, description="Room not found")

    tracker_data = TrackerData(room)
    bingo_data = _load_bingo_board(tracker, tracker_data.get_seed_name())

    return {
        "available": bingo_data is not None,
        "seed": tracker_data.get_seed_name(),
    }


# Helper functions

def _load_bingo_board(tracker: UUID, seed_name: str) -> Dict[str, Any] | None:
    """
    Load bingo board from file.

    Tries:
    1. Tracker-specific uploaded file
    2. Seed-based file from output directory
    """
    # Try tracker-specific file first
    tracker_path = output_path(f"bingo_boards/{tracker}.json")
    if os.path.exists(tracker_path):
        with open(tracker_path, 'r') as f:
            return json.load(f)

    # Try seed-based file
    seed_pattern = f"*{seed_name}*_Bingo_*.json"
    import glob
    matches = glob.glob(output_path(seed_pattern))
    if matches:
        with open(matches[0], 'r') as f:
            return json.load(f)

    return None


def _save_bingo_board(tracker: UUID, bingo_data: Dict[str, Any]) -> None:
    """Save uploaded bingo board for a specific tracker."""
    os.makedirs(output_path("bingo_boards"), exist_ok=True)
    tracker_path = output_path(f"bingo_boards/{tracker}.json")

    with open(tracker_path, 'w') as f:
        json.dump(bingo_data, f, indent=2)


def _validate_bingo_data(data: Dict[str, Any]) -> bool:
    """Validate that uploaded data is a valid bingo board."""
    if "board" not in data:
        return False

    board = data["board"]
    if not isinstance(board, list) or len(board) != 5:
        return False

    for row in board:
        if not isinstance(row, list) or len(row) != 5:
            return False
        for tile in row:
            if not isinstance(tile, dict):
                return False
            if "location" not in tile or "player" not in tile:
                return False

    return True


def _process_bingo_board(
    board: List[List[Dict[str, Any]]],
    checked_locations: Dict[tuple, set],
    location_name_maps: Dict[str, Dict[str, int]]
) -> List[List[BingoTile]]:
    """
    Process bingo board and mark completed tiles.

    Args:
        board: Raw bingo board from JSON
        checked_locations: Dict of (team, player) -> set of checked location IDs
        location_name_maps: Dict of game -> location name to ID mapping

    Returns:
        Board with completion status added to each tile
    """
    processed_board = []

    for row in board:
        processed_row = []
        for tile in row:
            # Extract location name (strip player suffix if present)
            location_full = tile["location"]
            player = tile["player"]
            game = tile["game"]

            # Parse location name (remove " (Player N)" suffix)
            location_name = location_full
            if " (Player " in location_name:
                location_name = location_name[:location_name.rfind(" (Player ")]

            # Resolve location ID
            location_id = None
            if game in location_name_maps:
                location_id = location_name_maps[game].get(location_name)

            # Check if completed (check all teams for this player)
            completed = False
            if location_id is not None:
                for (team, checked_player), locs in checked_locations.items():
                    if checked_player == player and location_id in locs:
                        completed = True
                        break

            processed_tile: BingoTile = {
                "location": tile["location"],
                "player": player,
                "game": game,
                "sphere": tile.get("sphere", 0),
                "item": tile.get("item", "Unknown"),
                "location_id": location_id,
                "completed": completed,
            }
            processed_row.append(processed_tile)

        processed_board.append(processed_row)

    return processed_board


def _calculate_bingo_status(board: List[List[BingoTile]]) -> BingoStatus:
    """Calculate overall bingo completion statistics."""
    total_tiles = 25
    completed_tiles = sum(
        1 for row in board for tile in row if tile["completed"]
    )

    completed_lines = []

    # Check rows
    for i, row in enumerate(board):
        if all(tile["completed"] for tile in row):
            completed_lines.append(f"row_{i}")

    # Check columns
    for col in range(5):
        if all(board[row][col]["completed"] for row in range(5)):
            completed_lines.append(f"col_{col}")

    # Check main diagonal (top-left to bottom-right)
    if all(board[i][i]["completed"] for i in range(5)):
        completed_lines.append("diag_main")

    # Check anti-diagonal (top-right to bottom-left)
    if all(board[i][4-i]["completed"] for i in range(5)):
        completed_lines.append("diag_anti")

    return {
        "total_tiles": total_tiles,
        "completed_tiles": completed_tiles,
        "completion_percentage": (completed_tiles / total_tiles) * 100,
        "completed_lines": completed_lines,
    }
