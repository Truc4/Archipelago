"""
Archipelago Bingo Board Generator

Generates deterministic 5x5 bingo boards using playthrough sphere data.
Tiles are locations/checks weighted by sphere depth according to difficulty.
"""

import json
import logging
import random
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

from BaseClasses import MultiWorld, Location

logger = logging.getLogger("Bingo")


# Difficulty presets: (easy_weight, mid_weight, late_weight)
# These control the relative probability of selecting from each third of the sphere range
DIFFICULTY_PROFILES = {
    "easy": (5.0, 2.0, 0.5),      # Heavily favor early spheres
    "normal": (1.5, 3.0, 1.5),    # Favor mid-game spheres
    "hard": (0.5, 2.0, 5.0),      # Heavily favor late spheres
}


def generate_bingo_board(
    multiworld: MultiWorld,
    difficulty: str = "normal",
    mode: str = "coop",
    max_per_player: Optional[int] = None,
    max_per_sphere: Optional[int] = None,
) -> Dict:
    """
    Generate a deterministic 5x5 bingo board from playthrough spheres.

    Args:
        multiworld: The MultiWorld instance after fill and playthrough generation
        difficulty: "easy", "normal", or "hard" (controls sphere weighting)
        mode: "coop" or "race" (determines board generation strategy)
            - "coop": One shared board with locations from all players. Players work
                     together - each player completes their own locations on the shared board.
            - "race": Each player gets their own separate board with only their locations.
                     Players race to complete their individual boards first.
        max_per_player: Optional cap on tiles per player (None = auto-calculate for fairness)
        max_per_sphere: Optional cap on tiles per sphere (None = no limit)

    Returns:
        Dictionary containing board data suitable for JSON export
        For "coop" mode: single board dict
        For "race" mode: dict with player keys mapping to individual boards
    """
    if not hasattr(multiworld, 'spoiler') or not multiworld.spoiler.playthrough:
        raise ValueError("Bingo generation requires spoiler playthrough to be computed first")

    # Validate mode
    if mode not in ["coop", "race"]:
        raise ValueError(f"Invalid bingo mode '{mode}'. Must be 'coop' or 'race'")

    # Extract location candidates from playthrough spheres
    collection_spheres = _extract_collection_spheres_from_playthrough(multiworld)
    candidates = _extract_location_candidates(collection_spheres)

    if len(candidates) < 25:
        raise ValueError(f"Not enough reachable locations for bingo board (found {len(candidates)}, need 25)")

    logger.info(f"Bingo: Found {len(candidates)} location candidates across {len(collection_spheres)} spheres")

    # Handle different modes
    if mode == "coop":
        return _generate_coop_board(multiworld, candidates, difficulty, max_per_player, max_per_sphere)
    elif mode == "race":
        return _generate_race_boards(multiworld, candidates, difficulty, max_per_player, max_per_sphere)
    else:
        raise ValueError(f"Unsupported mode: {mode}")


def _generate_coop_board(
    multiworld: MultiWorld,
    candidates: List[Tuple[Location, int]],
    difficulty: str,
    max_per_player: Optional[int] = None,
    max_per_sphere: Optional[int] = None,
) -> Dict:
    """
    Generate a single cooperative board where all players work together.

    Each tile belongs to a specific player, but all players share the same board.
    Players work together to complete the board - each completes their own locations.
    """
    seed = _derive_bingo_seed(multiworld.seed, difficulty)
    rng = random.Random(seed)

    # Group candidates by player
    player_candidates = defaultdict(list)
    for location, sphere_idx in candidates:
        player_candidates[location.player].append((location, sphere_idx))

    # Log how many candidates each player has
    logger.info(f"Bingo (coop): Candidates per player: {', '.join(f'P{p}: {len(locs)}' for p, locs in sorted(player_candidates.items()))}")

    # Calculate fair distribution (e.g., 8-8-9 for 3 players)
    tiles_per_player = {}
    remaining_tiles = 25
    for player in sorted(player_candidates.keys()):
        players_left = multiworld.players - len(tiles_per_player)
        tiles_this_player = remaining_tiles // players_left
        tiles_per_player[player] = tiles_this_player
        remaining_tiles -= tiles_this_player

    logger.info(f"Bingo (coop): Target distribution: {', '.join(f'P{p}: {c}' for p, c in tiles_per_player.items())}")

    # Sample from each player independently
    selected_tiles = []
    for player in sorted(player_candidates.keys()):
        player_locs = player_candidates[player]
        target_count = tiles_per_player[player]

        # Calculate weights specifically for this player's locations
        player_weights = _calculate_weights(player_locs, difficulty)

        # Sample this player's tiles
        if len(player_locs) >= target_count:
            # Use weighted sampling without constraints
            player_tiles = _weighted_sample_tiles(
                player_locs,
                player_weights,
                seed + player,  # Different seed per player
                count=target_count,
                max_per_player=None,  # No limit since we're already filtering by player
                max_per_sphere=max_per_sphere
            )
            selected_tiles.extend(player_tiles)
        else:
            # Not enough locations for this player, take all available
            logger.warning(f"Bingo (coop): Player {player} has only {len(player_locs)} locations, needed {target_count}")
            selected_tiles.extend(player_locs)

    # Shuffle tiles to randomize board positions
    rng.shuffle(selected_tiles)

    # Build board data structure
    board_data = _build_board_data(multiworld, selected_tiles, difficulty, mode="coop")

    # Log final distribution
    player_counts = defaultdict(int)
    for location, _ in selected_tiles:
        player_counts[location.player] += 1
    distribution_str = ", ".join(f"P{p}: {count}" for p, count in sorted(player_counts.items()))
    logger.info(f"Bingo (coop): Generated {difficulty} board with seed {seed} - Final distribution: {distribution_str}")

    return board_data


def _generate_race_boards(
    multiworld: MultiWorld,
    candidates: List[Tuple[Location, int]],
    difficulty: str,
    max_per_player: Optional[int] = None,
    max_per_sphere: Optional[int] = None,
) -> Dict:
    """
    Generate individual race boards for each player.

    Each player gets their own 5x5 board containing only their locations.
    Players race to complete their individual boards first.

    TODO: RACE MODE IMPLEMENTATION
    This mode is not yet implemented. Required changes:

    1. Filter candidates by player:
       - For each player, create a separate candidate list
       - candidates_p1 = [(loc, sphere) for loc, sphere in candidates if loc.player == 1]

    2. Validate each player has enough locations:
       - if len(candidates_pN) < 25: raise error or warning
       - Consider: allow smaller boards (3x3, 4x4) if < 25 locations?

    3. Generate N separate boards:
       - for player in range(1, multiworld.players + 1):
       -     seed = _derive_bingo_seed(multiworld.seed + player, difficulty)
       -     board = generate board for this player

    4. Return format:
       - Return dict with player keys: {1: board_data_p1, 2: board_data_p2, ...}
       - OR: return list of boards: [board_data_p1, board_data_p2, ...]

    5. Update JSON output:
       - Write separate files: AP_seed_Bingo_race_P1.json, AP_seed_Bingo_race_P2.json
       - OR: Write one file with nested structure

    6. Update text formatting:
       - Either: multiple boards in spoiler (one per player)
       - OR: side-by-side comparison view

    7. Consider edge cases:
       - Single player game (race mode doesn't make sense - fallback to coop?)
       - Player with < 25 locations (error? smaller board? fill with dummy tiles?)
       - Very uneven location counts (P1 has 100 locs, P2 has 30)

    8. Update web tracker (see WebHostLib/templates/bingo_tracker.html):
       - Support displaying player-specific boards
       - Filter tracker to show only current player's board
       - OR: show all boards side-by-side for comparison
    """
    raise NotImplementedError(
        "Race mode is not yet implemented. Use mode='coop' instead. "
        "See TODO comments in _generate_race_boards() for implementation details."
    )


def _extract_collection_spheres_from_playthrough(multiworld: MultiWorld) -> List[List[Location]]:
    """
    Reconstruct collection_spheres from the playthrough dictionary.

    The playthrough dict maps sphere numbers (as strings) to location dictionaries.
    We need to convert this back to a list of location lists with sphere indices.
    """
    playthrough = multiworld.spoiler.playthrough
    spheres = []

    # Sphere "0" is precollected items (skip it for bingo purposes)
    sphere_numbers = sorted([int(k) for k in playthrough.keys() if k != "0"])

    for sphere_num in sphere_numbers:
        sphere_key = str(sphere_num)
        if sphere_key not in playthrough:
            continue

        sphere_dict = playthrough[sphere_key]
        sphere_locations = []

        # playthrough[sphere_key] is a dict of {location_str: item_str}
        # We need to resolve these back to Location objects
        for location_str in sphere_dict.keys():
            # Parse location string format: "Location Name (Player N)"
            location = _parse_location_from_string(multiworld, location_str)
            if location:
                sphere_locations.append(location)

        spheres.append(sphere_locations)

    return spheres


def _parse_location_from_string(multiworld: MultiWorld, location_str: str) -> Optional[Location]:
    """
    Parse a location string from the playthrough and return the corresponding Location object.

    Handles two formats:
    - "Location Name (PlayerName)" for multiplayer
    - "Location Name" for single player
    """
    try:
        # Handle multi-player format: "Location Name (PlayerName)"
        if " (" in location_str and location_str.endswith(")"):
            # Extract location name and player name
            location_name = location_str[:location_str.rfind(" (")].strip()
            player_name = location_str[location_str.rfind(" (") + 2:-1].strip()

            # Find player number by name
            player = None
            for p in range(1, multiworld.players + 1):
                if multiworld.get_player_name(p) == player_name:
                    player = p
                    break

            if player is None:
                logger.warning(f"Bingo: Could not find player '{player_name}' for location '{location_str}'")
                return None
        else:
            # Single player format: just the location name
            location_name = location_str
            player = 1

        # Find the location in the multiworld
        for location in multiworld.get_locations(player):
            if location.name == location_name:
                return location

        logger.warning(f"Bingo: Could not resolve location '{location_str}' for player {player}")
        return None
    except Exception as e:
        logger.warning(f"Bingo: Error parsing location '{location_str}': {e}")
        return None


def _extract_location_candidates(collection_spheres: List[List[Location]]) -> List[Tuple[Location, int]]:
    """
    Extract all locations from collection spheres with their sphere index.

    Returns:
        List of (Location, sphere_index) tuples
    """
    candidates = []
    for sphere_idx, sphere in enumerate(collection_spheres):
        for location in sphere:
            # Filter out event locations (they have no physical presence)
            if not location.is_event and location.show_in_spoiler:
                candidates.append((location, sphere_idx))

    return candidates


def _calculate_weights(
    candidates: List[Tuple[Location, int]],
    difficulty: str
) -> List[float]:
    """
    Calculate sampling weights for each candidate based on sphere depth and difficulty.

    The difficulty profile determines how sphere depth maps to weight:
    - Easy: exponentially favor earlier spheres
    - Normal: favor middle spheres (bell curve)
    - Hard: exponentially favor later spheres
    """
    if difficulty not in DIFFICULTY_PROFILES:
        logger.warning(f"Unknown difficulty '{difficulty}', using 'normal'")
        difficulty = "normal"

    early_weight, mid_weight, late_weight = DIFFICULTY_PROFILES[difficulty]

    # Find sphere range
    max_sphere = max(sphere_idx for _, sphere_idx in candidates)
    total_spheres = max_sphere + 1

    # Calculate weight for each candidate based on its sphere position
    weights = []
    for location, sphere_idx in candidates:
        # Normalize sphere position to [0.0, 1.0]
        normalized_position = sphere_idx / max(1, max_sphere)

        # Divide into thirds: early (0-0.33), mid (0.33-0.66), late (0.66-1.0)
        if normalized_position < 0.33:
            weight = early_weight
        elif normalized_position < 0.66:
            weight = mid_weight
        else:
            weight = late_weight

        # Optional: Add smooth interpolation between sections
        # This prevents sharp boundaries between difficulty regions
        section_position = (normalized_position % 0.33) / 0.33
        if normalized_position < 0.33:
            weight = early_weight + (mid_weight - early_weight) * section_position * 0.3
        elif normalized_position < 0.66:
            weight = mid_weight + (late_weight - mid_weight) * section_position * 0.3

        weights.append(weight)

    return weights


def _weighted_sample_tiles(
    candidates: List[Tuple[Location, int]],
    weights: List[float],
    seed: int,
    count: int = 25,
    max_per_player: Optional[int] = None,
    max_per_sphere: Optional[int] = None,
) -> List[Tuple[Location, int]]:
    """
    Select tiles using weighted random sampling with optional constraints.

    Deterministic: same seed + candidates + weights = same output.
    """
    rng = random.Random(seed)
    selected = []
    remaining_candidates = candidates.copy()
    remaining_weights = weights.copy()

    # Track constraints
    player_counts = defaultdict(int)
    sphere_counts = defaultdict(int)

    while len(selected) < count and remaining_candidates:
        # Weighted random choice
        chosen = rng.choices(remaining_candidates, weights=remaining_weights, k=1)[0]
        location, sphere_idx = chosen

        # Check constraints
        if max_per_player and player_counts[location.player] >= max_per_player:
            # Remove all locations from this player and retry
            indices_to_remove = [i for i, (loc, _) in enumerate(remaining_candidates)
                               if loc.player == location.player]
            for idx in sorted(indices_to_remove, reverse=True):
                remaining_candidates.pop(idx)
                remaining_weights.pop(idx)
            continue

        if max_per_sphere and sphere_counts[sphere_idx] >= max_per_sphere:
            # Remove all locations from this sphere and retry
            indices_to_remove = [i for i, (_, sph) in enumerate(remaining_candidates)
                               if sph == sphere_idx]
            for idx in sorted(indices_to_remove, reverse=True):
                remaining_candidates.pop(idx)
                remaining_weights.pop(idx)
            continue

        # Accept this tile
        selected.append(chosen)
        player_counts[location.player] += 1
        sphere_counts[sphere_idx] += 1

        # Remove from candidates
        idx = remaining_candidates.index(chosen)
        remaining_candidates.pop(idx)
        remaining_weights.pop(idx)

    if len(selected) < count:
        logger.warning(f"Bingo: Could only select {len(selected)}/{count} tiles due to constraints")

    return selected


def _derive_bingo_seed(multiworld_seed: int, difficulty: str) -> int:
    """
    Derive a deterministic bingo seed from the multiworld seed and difficulty.
    """
    # Use a simple hash to combine seed and difficulty
    difficulty_hash = hash(difficulty) & 0xFFFFFFFF  # Keep it 32-bit
    return (multiworld_seed + difficulty_hash) & 0xFFFFFFFF


def _build_board_data(
    multiworld: MultiWorld,
    tiles: List[Tuple[Location, int]],
    difficulty: str,
    mode: str = "coop"
) -> Dict:
    """
    Build the final board data structure for JSON export.
    """
    # Arrange tiles in 5x5 grid (row-major order)
    grid = []
    for row_idx in range(5):
        row = []
        for col_idx in range(5):
            tile_idx = row_idx * 5 + col_idx
            if tile_idx < len(tiles):
                location, sphere_idx = tiles[tile_idx]

                # Format player name for multiplayer
                if multiworld.players > 1:
                    player_name = multiworld.get_player_name(location.player)
                    location_display = f"{location.name} ({player_name})"
                else:
                    location_display = location.name

                tile_data = {
                    "location": location_display,
                    "player": location.player,
                    "game": location.game,
                    "sphere": sphere_idx + 1,  # 1-indexed for display
                    "item": location.item.name if location.item else "Nothing"
                }
            else:
                tile_data = {"location": "Empty", "player": 0, "game": "", "sphere": 0, "item": ""}

            row.append(tile_data)
        grid.append(row)

    board_data = {
        "version": "1.0",
        "seed": multiworld.seed,
        "difficulty": difficulty,
        "mode": mode,
        "board": grid,
        "metadata": {
            "total_spheres": max(tile[1] for tile in tiles) + 1 if tiles else 0,
            "players": multiworld.players
        }
    }

    return board_data


def write_bingo_board_json(board_data: Dict, output_path: str) -> None:
    """
    Write the bingo board data to a JSON file.
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(board_data, f, indent=2, ensure_ascii=False)

    logger.info(f"Bingo: Wrote board to {output_path}")


def format_bingo_board_text(board_data: Dict) -> str:
    """
    Format the bingo board as human-readable text for appending to spoiler.

    Returns a formatted string with the 5x5 board layout.
    """
    lines = []
    lines.append("\n\n" + "="*80)
    mode = board_data.get('mode', 'coop').upper()
    lines.append(f"BINGO BOARD - Mode: {mode} - Difficulty: {board_data['difficulty'].upper()}")
    lines.append("="*80 + "\n")

    grid = board_data["board"]

    # Calculate column widths
    col_widths = [0] * 5
    for row in grid:
        for col_idx, tile in enumerate(row):
            location_str = tile["location"]
            col_widths[col_idx] = max(col_widths[col_idx], len(location_str))

    # Add padding
    col_widths = [min(w + 2, 40) for w in col_widths]  # Cap at 40 chars per column

    # Print header
    for row_idx, row in enumerate(grid):
        row_strs = []
        for col_idx, tile in enumerate(row):
            location_str = tile["location"]
            sphere_str = f"[S{tile['sphere']}]"

            # Truncate if too long
            max_len = col_widths[col_idx] - len(sphere_str) - 1
            if len(location_str) > max_len:
                location_str = location_str[:max_len-3] + "..."

            cell_str = f"{location_str} {sphere_str}"
            row_strs.append(cell_str.ljust(col_widths[col_idx]))

        lines.append(" | ".join(row_strs))

        # Add separator between rows (except after last row)
        if row_idx < 4:
            lines.append("-" * (sum(col_widths) + 12))  # 12 = 4 separators * 3 chars

    lines.append("\n" + "="*80)
    lines.append("Legend: [SN] = Sphere N (progression depth)")
    lines.append("="*80)

    return "\n".join(lines)
