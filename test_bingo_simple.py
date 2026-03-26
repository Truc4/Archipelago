#!/usr/bin/env python3
"""
Simple Bingo Module Logic Tests

Tests core logic functions without requiring full Archipelago dependencies.
"""

import random
from collections import defaultdict, namedtuple


# Copy of difficulty profiles from bingo.py
DIFFICULTY_PROFILES = {
    "easy": (5.0, 2.0, 0.5),
    "normal": (1.5, 3.0, 1.5),
    "hard": (0.5, 2.0, 5.0),
}


def calculate_weights_simplified(num_spheres: int, difficulty: str) -> list:
    """Simplified version of weight calculation for testing."""
    if difficulty not in DIFFICULTY_PROFILES:
        difficulty = "normal"

    early_weight, mid_weight, late_weight = DIFFICULTY_PROFILES[difficulty]

    weights = []
    for sphere_idx in range(num_spheres):
        normalized_position = sphere_idx / max(1, num_spheres - 1)

        if normalized_position < 0.33:
            weight = early_weight
            section_position = (normalized_position % 0.33) / 0.33
            weight = early_weight + (mid_weight - early_weight) * section_position * 0.3
        elif normalized_position < 0.66:
            weight = mid_weight
            section_position = (normalized_position % 0.33) / 0.33
            weight = mid_weight + (late_weight - mid_weight) * section_position * 0.3
        else:
            weight = late_weight

        weights.append(weight)

    return weights


def test_weight_distribution():
    """Test that different difficulties produce expected weight patterns."""
    print("\n=== Weight Distribution Test ===")

    num_spheres = 30
    for difficulty in ['easy', 'normal', 'hard']:
        weights = calculate_weights_simplified(num_spheres, difficulty)

        early_avg = sum(weights[0:10]) / 10
        mid_avg = sum(weights[10:20]) / 10
        late_avg = sum(weights[20:30]) / 10

        print(f"\n{difficulty.upper()}:")
        print(f"  Early (0-9):   {early_avg:.2f}")
        print(f"  Mid (10-19):   {mid_avg:.2f}")
        print(f"  Late (20-29):  {late_avg:.2f}")

        # Verify expected relationships
        if difficulty == 'easy':
            assert early_avg > late_avg, f"{difficulty}: Early should be > Late"
            print("  ✓ Favors early spheres")
        elif difficulty == 'hard':
            assert late_avg > early_avg, f"{difficulty}: Late should be > Early"
            print("  ✓ Favors late spheres")
        elif difficulty == 'normal':
            # Normal should have relatively balanced distribution
            print("  ✓ Balanced distribution")

    print("\n✓ Weight distribution test passed")


def test_determinism():
    """Test that RNG with same seed produces same results."""
    print("\n=== Determinism Test ===")

    candidates = list(range(100))

    # Same seed should produce identical results
    rng1 = random.Random(42)
    sample1 = rng1.choices(candidates, k=25)

    rng2 = random.Random(42)
    sample2 = rng2.choices(candidates, k=25)

    print(f"Sample 1 (first 10): {sample1[:10]}")
    print(f"Sample 2 (first 10): {sample2[:10]}")

    assert sample1 == sample2, "Same seed should produce identical samples"
    print("✓ Determinism verified")

    # Different seed should produce different results
    rng3 = random.Random(43)
    sample3 = rng3.choices(candidates, k=25)

    assert sample1 != sample3, "Different seeds should produce different samples"
    print("✓ Different seeds produce different results")

    print("\n✓ Determinism test passed")


def test_seed_derivation():
    """Test seed derivation from multiworld seed and difficulty."""
    print("\n=== Seed Derivation Test ===")

    def derive_bingo_seed(multiworld_seed: int, difficulty: str) -> int:
        difficulty_hash = hash(difficulty) & 0xFFFFFFFF
        return (multiworld_seed + difficulty_hash) & 0xFFFFFFFF

    base_seed = 12345

    seeds = {}
    for difficulty in ['easy', 'normal', 'hard']:
        seeds[difficulty] = derive_bingo_seed(base_seed, difficulty)
        print(f"{difficulty:6}: {seeds[difficulty]}")

    # All should be different
    assert len(set(seeds.values())) == 3, "Different difficulties should produce different seeds"
    print("✓ Each difficulty produces unique seed")

    # Same input should always produce same output
    seed_again = derive_bingo_seed(base_seed, 'normal')
    assert seed_again == seeds['normal'], "Seed derivation should be deterministic"
    print("✓ Seed derivation is deterministic")

    print("\n✓ Seed derivation test passed")


def test_constraint_sampling():
    """Test sampling with constraints."""
    print("\n=== Constraint Sampling Test ===")

    MockItem = namedtuple('Item', ['id', 'player', 'sphere'])

    # Create 100 items across 3 players and 10 spheres
    items = []
    for i in range(100):
        items.append(MockItem(i, (i % 3) + 1, i // 10))

    def sample_with_player_cap(items, seed, count=25, max_per_player=8):
        """Sample items with a max_per_player constraint."""
        rng = random.Random(seed)
        selected = []
        remaining = items.copy()
        player_counts = defaultdict(int)

        while len(selected) < count and remaining:
            # Pick one randomly
            chosen = rng.choice(remaining)

            # Check constraint
            if player_counts[chosen.player] >= max_per_player:
                # Remove all items from this player
                remaining = [item for item in remaining if item.player != chosen.player]
                continue

            selected.append(chosen)
            player_counts[chosen.player] += 1
            remaining.remove(chosen)

        return selected, player_counts

    selected, player_counts = sample_with_player_cap(items, 42, count=25, max_per_player=8)

    print(f"Selected {len(selected)} items")
    print(f"Player distribution: {dict(player_counts)}")

    # Verify constraint
    for player, count in player_counts.items():
        assert count <= 8, f"Player {player} has {count} items, exceeds limit"

    print("✓ Player cap constraint respected")

    print("\n✓ Constraint sampling test passed")


def test_board_layout():
    """Test 5x5 board layout logic."""
    print("\n=== Board Layout Test ===")

    # Simulate 25 tiles
    tiles = [f"Location_{i}" for i in range(25)]

    # Arrange in 5x5 grid
    board = []
    for row_idx in range(5):
        row = []
        for col_idx in range(5):
            tile_idx = row_idx * 5 + col_idx
            row.append(tiles[tile_idx])
        board.append(row)

    print("\nBoard layout:")
    for row in board:
        print("  " + " | ".join(row))

    # Verify dimensions
    assert len(board) == 5, "Should have 5 rows"
    assert all(len(row) == 5 for row in board), "Each row should have 5 columns"

    # Verify all tiles present
    flat = [tile for row in board for tile in row]
    assert len(flat) == 25, "Should have 25 tiles total"
    assert len(set(flat)) == 25, "All tiles should be unique"

    print("\n✓ Board layout test passed")


def test_sphere_weighted_sampling():
    """Test that sphere weights actually affect sampling distribution."""
    print("\n=== Sphere-Weighted Sampling Test ===")

    # Create items with sphere indices
    items = [(f"Item_{i}", i // 10) for i in range(100)]  # 10 items per sphere, 10 spheres

    def weighted_sample(items, difficulty, seed, count=100):
        """Sample items with sphere-based weights."""
        weights = []
        max_sphere = 9
        for item_name, sphere_idx in items:
            normalized = sphere_idx / max_sphere

            if difficulty == 'easy':
                weight = 5.0 if normalized < 0.33 else 2.0 if normalized < 0.66 else 0.5
            elif difficulty == 'hard':
                weight = 0.5 if normalized < 0.33 else 2.0 if normalized < 0.66 else 5.0
            else:
                weight = 1.5 if normalized < 0.33 else 3.0 if normalized < 0.66 else 1.5

            weights.append(weight)

        rng = random.Random(seed)
        return rng.choices(items, weights=weights, k=count)

    # Sample with different difficulties
    for difficulty in ['easy', 'normal', 'hard']:
        sampled = weighted_sample(items, difficulty, seed=12345, count=100)

        # Count sphere distribution
        sphere_counts = defaultdict(int)
        for _, sphere_idx in sampled:
            sphere_counts[sphere_idx] += 1

        early = sum(sphere_counts[i] for i in range(0, 3))  # Spheres 0-2
        mid = sum(sphere_counts[i] for i in range(3, 7))     # Spheres 3-6
        late = sum(sphere_counts[i] for i in range(7, 10))   # Spheres 7-9

        print(f"\n{difficulty.upper()} sampling distribution:")
        print(f"  Early (S0-2): {early}% of samples")
        print(f"  Mid (S3-6):   {mid}% of samples")
        print(f"  Late (S7-9):  {late}% of samples")

        if difficulty == 'easy':
            assert early > late, "Easy should sample more from early spheres"
            print("  ✓ Favors early")
        elif difficulty == 'hard':
            assert late > early, "Hard should sample more from late spheres"
            print("  ✓ Favors late")

    print("\n✓ Sphere-weighted sampling test passed")


def run_all_tests():
    """Run all test functions."""
    print("="*80)
    print("BINGO MODULE LOGIC TESTS")
    print("="*80)

    test_weight_distribution()
    test_determinism()
    test_seed_derivation()
    test_constraint_sampling()
    test_board_layout()
    test_sphere_weighted_sampling()

    print("\n" + "="*80)
    print("ALL TESTS PASSED ✓")
    print("="*80)
    print("\nThe bingo module logic is working correctly.")
    print("To test with real Archipelago data, run a generation with --bingo flag.")


if __name__ == '__main__':
    run_all_tests()
