#!/usr/bin/env python3
"""
Test bingo with a simulated real-world scenario
"""

import sys
import os

# Add the Archipelago directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unittest.mock import Mock
import bingo

def test_with_simulated_playthrough():
    """Test with simulated real playthrough data structure"""
    print("Testing bingo with simulated real Archipelago playthrough...")

    # Create a mock multiworld similar to real Archipelago
    multiworld = Mock()
    multiworld.seed = 123456
    multiworld.players = 1

    # Create mock locations
    locations = []
    for i in range(1, 51):  # 50 locations
        loc = Mock()
        loc.name = f"Location_{i}"
        loc.player = 1
        loc.game = "A Link to the Past"
        loc.is_event = False
        loc.show_in_spoiler = True

        item = Mock()
        item.name = f"Item_{i}"
        loc.item = item

        locations.append(loc)

    # Mock get_locations
    multiworld.get_locations = Mock(return_value=locations)
    multiworld.get_player_name = Mock(return_value="Player1")

    # Create playthrough data structure (matches real Archipelago format)
    playthrough = {
        "0": {},  # Precollected items
    }

    # Add 10 spheres with 5 locations each
    for sphere_num in range(1, 11):
        sphere_dict = {}
        for loc_idx in range(5):
            overall_idx = (sphere_num - 1) * 5 + loc_idx + 1
            if overall_idx <= 50:
                location_str = f"Location_{overall_idx}"
                item_str = f"Item_{overall_idx}"
                sphere_dict[location_str] = item_str
        playthrough[str(sphere_num)] = sphere_dict

    # Create spoiler with playthrough
    spoiler = Mock()
    spoiler.playthrough = playthrough
    multiworld.spoiler = spoiler

    # Try to generate bingo
    try:
        print(f"\nGenerating bingo board with {len(playthrough)-1} spheres...")
        board_data = bingo.generate_bingo_board(multiworld, 'normal')

        print(f"✓ Board generated successfully!")
        print(f"  Difficulty: {board_data['difficulty']}")
        print(f"  Seed: {board_data['seed']}")
        print(f"  Board dimensions: {len(board_data['board'])}x{len(board_data['board'][0])}")

        # Count unique locations
        unique_locs = set()
        for row in board_data['board']:
            for tile in row:
                if tile['location'] != 'Empty':
                    unique_locs.add(tile['location'])

        print(f"  Unique locations: {len(unique_locs)}")

        if len(unique_locs) < 25:
            print(f"\n⚠ WARNING: Only got {len(unique_locs)} unique locations (need 25)")
            print("This suggests there aren't enough valid locations in the playthrough")
            return False

        return True

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_with_simulated_playthrough()
    sys.exit(0 if success else 1)
