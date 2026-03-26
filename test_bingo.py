#!/usr/bin/env python3
"""
Bingo Module Test Script

Tests the bingo generator with mock data to verify:
- Weight calculations
- Deterministic sampling
- Board generation
- JSON output
"""

import json
import tempfile
from collections import namedtuple
from unittest.mock import Mock

import bingo


# Mock classes to simulate Archipelago structures
MockLocation = namedtuple('Location', ['name', 'player', 'game', 'item', 'is_event', 'show_in_spoiler'])
MockItem = namedtuple('Item', ['name'])


def create_mock_multiworld(num_players=2, num_spheres=10, locations_per_sphere=5, seed=12345):
    """Create a mock multiworld with sphere data."""
    multiworld = Mock()
    multiworld.seed = seed
    multiworld.players = num_players

    # Create mock playthrough dictionary
    playthrough = {"0": []}  # Sphere 0 is precollected items

    all_locations = []
    location_counter = 0

    for sphere_num in range(1, num_spheres + 1):
        sphere_dict = {}
        for i in range(locations_per_sphere):
            location_counter += 1
            player = (location_counter % num_players) + 1
            game = f"Game{player}"

            location_name = f"Location_{location_counter}"
            item_name = f"Item_{location_counter}"

            # Format as playthrough string
            if num_players > 1:
                location_str = f"{location_name} (Player {player})"
            else:
                location_str = location_name

            sphere_dict[location_str] = item_name

            # Create mock location object
            mock_item = MockItem(name=item_name)
            mock_loc = MockLocation(
                name=location_name,
                player=player,
                game=game,
                item=mock_item,
                is_event=False,
                show_in_spoiler=True
            )
            all_locations.append((mock_loc, sphere_num))

        playthrough[str(sphere_num)] = sphere_dict

    # Create spoiler mock
    spoiler = Mock()
    spoiler.playthrough = playthrough
    multiworld.spoiler = spoiler

    # Mock get_player_name
    multiworld.get_player_name = lambda p: f"Player{p}"

    # Mock get_locations
    def get_locations(player=None):
        if player is None:
            return [loc for loc, _ in all_locations]
        return [loc for loc, _ in all_locations if loc.player == player]

    multiworld.get_locations = get_locations

    return multiworld, all_locations


def test_weight_calculation():
    """Test that difficulty profiles produce different weight distributions."""
    print("\n=== Testing Weight Calculation ===")

    # Create candidates with even sphere distribution
    candidates = [(Mock(), sphere) for sphere in range(0, 30)]

    for difficulty in ['easy', 'normal', 'hard']:
        weights = bingo._calculate_weights(candidates, difficulty)

        # Calculate average weight by third
        early_avg = sum(weights[0:10]) / 10
        mid_avg = sum(weights[10:20]) / 10
        late_avg = sum(weights[20:30]) / 10

        print(f"\n{difficulty.upper()} difficulty:")
        print(f"  Early (spheres 0-9):  avg weight = {early_avg:.2f}")
        print(f"  Mid (spheres 10-19):  avg weight = {mid_avg:.2f}")
        print(f"  Late (spheres 20-29): avg weight = {late_avg:.2f}")

        # Verify expected relationships
        if difficulty == 'easy':
            assert early_avg > mid_avg > late_avg, "Easy should favor early spheres"
        elif difficulty == 'hard':
            assert late_avg > mid_avg > early_avg, "Hard should favor late spheres"

    print("\n✓ Weight calculation tests passed")


def test_deterministic_sampling():
    """Test that sampling with the same seed produces the same results."""
    print("\n=== Testing Deterministic Sampling ===")

    multiworld, all_locations = create_mock_multiworld(seed=99999)
    candidates = all_locations  # Use all mock locations

    weights = [1.0] * len(candidates)  # Equal weights for simplicity

    # Sample twice with same seed
    seed = 42
    tiles1 = bingo._weighted_sample_tiles(candidates, weights, seed, count=25)
    tiles2 = bingo._weighted_sample_tiles(candidates, weights, seed, count=25)

    print(f"Sample 1 locations: {[loc.name for loc, _ in tiles1[:5]]}...")
    print(f"Sample 2 locations: {[loc.name for loc, _ in tiles2[:5]]}...")

    assert tiles1 == tiles2, "Same seed should produce identical samples"

    # Sample with different seed should produce different results
    tiles3 = bingo._weighted_sample_tiles(candidates, weights, seed + 1, count=25)
    print(f"Sample 3 locations: {[loc.name for loc, _ in tiles3[:5]]}...")

    assert tiles1 != tiles3, "Different seeds should produce different samples"

    print("\n✓ Deterministic sampling tests passed")


def test_constraint_enforcement():
    """Test that max_per_player and max_per_sphere constraints work."""
    print("\n=== Testing Constraint Enforcement ===")

    multiworld, all_locations = create_mock_multiworld(
        num_players=3,
        num_spheres=10,
        locations_per_sphere=5
    )

    candidates = all_locations
    weights = [1.0] * len(candidates)

    # Test max_per_player constraint
    tiles = bingo._weighted_sample_tiles(
        candidates, weights, seed=12345, count=25, max_per_player=5
    )

    player_counts = {}
    for loc, _ in tiles:
        player_counts[loc.player] = player_counts.get(loc.player, 0) + 1

    print(f"\nPlayer distribution (max_per_player=5): {player_counts}")
    for player, count in player_counts.items():
        assert count <= 5, f"Player {player} has {count} tiles, exceeds limit of 5"

    # Test max_per_sphere constraint
    tiles = bingo._weighted_sample_tiles(
        candidates, weights, seed=12345, count=25, max_per_sphere=3
    )

    sphere_counts = {}
    for _, sphere in tiles:
        sphere_counts[sphere] = sphere_counts.get(sphere, 0) + 1

    print(f"Sphere distribution (max_per_sphere=3): {sphere_counts}")
    for sphere, count in sphere_counts.items():
        assert count <= 3, f"Sphere {sphere} has {count} tiles, exceeds limit of 3"

    print("\n✓ Constraint enforcement tests passed")


def test_board_generation():
    """Test full board generation pipeline."""
    print("\n=== Testing Board Generation ===")

    multiworld, _ = create_mock_multiworld(
        num_players=2,
        num_spheres=15,
        locations_per_sphere=5,
        seed=777
    )

    for difficulty in ['easy', 'normal', 'hard']:
        print(f"\nGenerating {difficulty} board...")
        board_data = bingo.generate_bingo_board(multiworld, difficulty)

        # Validate structure
        assert board_data['difficulty'] == difficulty
        assert board_data['seed'] == 777
        assert len(board_data['board']) == 5, "Should have 5 rows"
        assert all(len(row) == 5 for row in board_data['board']), "Each row should have 5 tiles"

        # Check for duplicates
        locations_set = set()
        for row in board_data['board']:
            for tile in row:
                loc_str = tile['location']
                if loc_str != "Empty":
                    assert loc_str not in locations_set, f"Duplicate location: {loc_str}"
                    locations_set.add(loc_str)

        print(f"  ✓ {difficulty} board has {len(locations_set)} unique locations")

        # Print sphere distribution
        sphere_counts = {}
        for row in board_data['board']:
            for tile in row:
                if tile['sphere'] > 0:
                    sphere_counts[tile['sphere']] = sphere_counts.get(tile['sphere'], 0) + 1

        print(f"  Sphere distribution: {dict(sorted(sphere_counts.items()))}")

    print("\n✓ Board generation tests passed")


def test_json_output():
    """Test JSON serialization."""
    print("\n=== Testing JSON Output ===")

    multiworld, _ = create_mock_multiworld(seed=123)
    board_data = bingo.generate_bingo_board(multiworld, 'normal')

    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        bingo.write_bingo_board_json(board_data, f.name)
        temp_path = f.name

    # Read back and verify
    with open(temp_path, 'r') as f:
        loaded_data = json.load(f)

    assert loaded_data == board_data, "Loaded JSON should match original data"
    print(f"✓ JSON successfully written to {temp_path}")
    print(f"  File size: {len(json.dumps(board_data, indent=2))} bytes")

    print("\n✓ JSON output tests passed")


def test_text_formatting():
    """Test text board formatting for spoiler."""
    print("\n=== Testing Text Formatting ===")

    multiworld, _ = create_mock_multiworld(seed=456)
    board_data = bingo.generate_bingo_board(multiworld, 'normal')

    text = bingo.format_bingo_board_text(board_data)

    # Verify it contains expected elements
    assert "BINGO BOARD" in text
    assert "NORMAL" in text
    assert "[S" in text  # Sphere indicators
    assert "Location_" in text  # At least one location

    print("\nFormatted text preview:")
    print(text[:500])  # Print first 500 chars

    print("\n✓ Text formatting tests passed")


def test_seed_derivation():
    """Test that bingo seeds are derived correctly."""
    print("\n=== Testing Seed Derivation ===")

    seed1 = bingo._derive_bingo_seed(12345, 'easy')
    seed2 = bingo._derive_bingo_seed(12345, 'normal')
    seed3 = bingo._derive_bingo_seed(12345, 'hard')

    print(f"Base seed: 12345")
    print(f"  Easy:   {seed1}")
    print(f"  Normal: {seed2}")
    print(f"  Hard:   {seed3}")

    # Different difficulties should produce different seeds
    assert seed1 != seed2 != seed3, "Different difficulties should have different seeds"

    # Same seed + difficulty should always produce same bingo seed
    seed1_again = bingo._derive_bingo_seed(12345, 'easy')
    assert seed1 == seed1_again, "Seed derivation should be deterministic"

    print("\n✓ Seed derivation tests passed")


def run_all_tests():
    """Run all test suites."""
    print("="*80)
    print("BINGO MODULE TEST SUITE")
    print("="*80)

    test_weight_calculation()
    test_deterministic_sampling()
    test_constraint_enforcement()
    test_board_generation()
    test_json_output()
    test_text_formatting()
    test_seed_derivation()

    print("\n" + "="*80)
    print("ALL TESTS PASSED ✓")
    print("="*80)


if __name__ == '__main__':
    run_all_tests()
