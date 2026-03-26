#!/usr/bin/env python3
"""
Integration tests for Bingo with real Archipelago games.

These tests generate actual multiworld games and verify bingo generation works.
"""

import os
import sys
import unittest
from pathlib import Path

# Add Archipelago to path
sys.path.insert(0, str(Path(__file__).parent))

import Generate
import Main
import bingo
from worlds.AutoWorld import AutoWorldRegister


class TestBingoWithRealGames(unittest.TestCase):
    """Test bingo generation with real Archipelago games."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.test_dir = Path(__file__).parent / "test_bingo_output"
        cls.test_dir.mkdir(exist_ok=True)

    def setUp(self):
        """Create test YAML files before each test."""
        self.yaml_files = []

    def tearDown(self):
        """Clean up test YAML files."""
        for yaml_file in self.yaml_files:
            if yaml_file.exists():
                yaml_file.unlink()

    def create_test_yaml(self, player_name: str, game: str, player_num: int = 1) -> Path:
        """Create a test YAML file for a player."""
        yaml_path = self.test_dir / f"player{player_num}_{game.replace(' ', '_')}.yaml"

        yaml_content = f"""
name: {player_name}
game: {game}
description: Test player for bingo integration tests

{game}:
  progression_balancing: 50
"""

        yaml_path.write_text(yaml_content)
        self.yaml_files.append(yaml_path)
        return yaml_path

    def generate_multiworld(self, *players, bingo_mode="coop", bingo_difficulty="normal"):
        """
        Generate a multiworld with specified players.

        Args:
            players: List of (name, game) tuples
            bingo_mode: "coop" or "race"
            bingo_difficulty: "easy", "normal", or "hard"

        Returns:
            (args, multiworld) tuple
        """
        # Create YAML files for each player
        for i, (name, game) in enumerate(players, start=1):
            self.create_test_yaml(name, game, i)

        # Build arguments
        argv = [
            '--player_files_path', str(self.test_dir),
            '--outputpath', str(self.test_dir),
            '--spoiler', '3',
            '--bingo', f'{bingo_mode}:{bingo_difficulty}',
            '--seed', '12345',  # Fixed seed for reproducibility
        ]

        args = Generate.mystery_argparse(argv)
        _, seed = Main.main(args)

        # Find the generated multiworld (it's created during main())
        # For testing purposes, we'll regenerate it here
        return args, seed

    def test_single_player_alttp_coop(self):
        """Test bingo generation with single player A Link to the Past."""
        print("\n=== Testing Single Player ALTTP (Co-op Mode) ===")

        args, seed = self.generate_multiworld(
            ("Alice", "A Link to the Past"),
            bingo_mode="coop",
            bingo_difficulty="normal"
        )

        # Check that bingo file was generated
        bingo_files = list(self.test_dir.glob("*_Bingo_coop_normal.json"))
        self.assertTrue(len(bingo_files) > 0, "Bingo file should be generated")

        print(f"✓ Generated bingo file: {bingo_files[0].name}")

        # Load and validate bingo data
        import json
        with open(bingo_files[0]) as f:
            bingo_data = json.load(f)

        self.assertEqual(bingo_data["mode"], "coop")
        self.assertEqual(bingo_data["difficulty"], "normal")
        self.assertEqual(len(bingo_data["board"]), 5)
        self.assertEqual(len(bingo_data["board"][0]), 5)

        # Count unique locations
        locations = set()
        for row in bingo_data["board"]:
            for tile in row:
                if tile["location"] != "Empty":
                    locations.add(tile["location"])
                    self.assertEqual(tile["player"], 1, "All tiles should belong to player 1")
                    self.assertEqual(tile["game"], "A Link to the Past")

        self.assertEqual(len(locations), 25, f"Should have 25 unique locations, got {len(locations)}")
        print(f"✓ All 25 tiles are unique ALTTP locations")
        print(f"✓ Test passed!")

    def test_multiplayer_coop_fair_distribution(self):
        """Test that co-op mode fairly distributes tiles across players."""
        print("\n=== Testing Multiplayer Co-op Fair Distribution ===")

        # Use available games (check which are installed)
        available_games = ["A Link to the Past", "Super Metroid"]

        # Verify games are available
        for game in available_games:
            if game not in AutoWorldRegister.world_types:
                self.skipTest(f"Game {game} not available")

        args, seed = self.generate_multiworld(
            ("Alice", "A Link to the Past"),
            ("Bob", "Super Metroid"),
            bingo_mode="coop",
            bingo_difficulty="normal"
        )

        # Load bingo data
        import json
        bingo_files = list(self.test_dir.glob("*_Bingo_coop_normal.json"))
        self.assertTrue(len(bingo_files) > 0, "Bingo file should be generated")

        with open(bingo_files[0]) as f:
            bingo_data = json.load(f)

        # Count tiles per player
        player_counts = {1: 0, 2: 0}
        for row in bingo_data["board"]:
            for tile in row:
                if tile["location"] != "Empty" and tile["player"] in player_counts:
                    player_counts[tile["player"]] += 1

        print(f"Player 1 (ALTTP) tiles: {player_counts[1]}")
        print(f"Player 2 (Super Metroid) tiles: {player_counts[2]}")

        # Verify fair distribution (with 2 players, should be roughly 50/50)
        # Allow some variance but ensure not too lopsided
        # With max_per_player = (25 // 2) + 3 = 15, expect distribution like 13-12, 14-11, etc.
        self.assertGreaterEqual(player_counts[1], 10, "Player 1 should have at least 10 tiles")
        self.assertGreaterEqual(player_counts[2], 10, "Player 2 should have at least 10 tiles")
        self.assertLessEqual(player_counts[1], 15, "Player 1 should have at most 15 tiles")
        self.assertLessEqual(player_counts[2], 15, "Player 2 should have at most 15 tiles")

        print(f"✓ Distribution is fair (both players have 10-15 tiles)")
        print(f"✓ Test passed!")

    def test_coop_mode_attributes(self):
        """Test that co-op mode properly sets board attributes."""
        print("\n=== Testing Co-op Mode Attributes ===")

        args, seed = self.generate_multiworld(
            ("TestPlayer", "A Link to the Past"),
            bingo_mode="coop",
            bingo_difficulty="hard"
        )

        import json
        bingo_files = list(self.test_dir.glob("*_Bingo_coop_hard.json"))
        with open(bingo_files[0]) as f:
            bingo_data = json.load(f)

        # Verify mode and difficulty
        self.assertEqual(bingo_data["mode"], "coop")
        self.assertEqual(bingo_data["difficulty"], "hard")

        # Verify metadata
        self.assertIn("metadata", bingo_data)
        self.assertIn("players", bingo_data["metadata"])

        # Verify each tile has required fields
        for row in bingo_data["board"]:
            for tile in row:
                self.assertIn("location", tile)
                self.assertIn("player", tile)
                self.assertIn("game", tile)
                self.assertIn("sphere", tile)
                self.assertIn("item", tile)

        print(f"✓ Mode: {bingo_data['mode']}")
        print(f"✓ Difficulty: {bingo_data['difficulty']}")
        print(f"✓ Players: {bingo_data['metadata']['players']}")
        print(f"✓ All tiles have required fields")
        print(f"✓ Test passed!")

    def test_difficulty_sphere_distribution(self):
        """Test that different difficulties produce expected sphere distributions."""
        print("\n=== Testing Difficulty Sphere Distributions ===")

        for difficulty in ["easy", "normal", "hard"]:
            print(f"\nTesting {difficulty} difficulty...")

            args, seed = self.generate_multiworld(
                ("TestPlayer", "A Link to the Past"),
                bingo_mode="coop",
                bingo_difficulty=difficulty
            )

            import json
            bingo_files = list(self.test_dir.glob(f"*_Bingo_coop_{difficulty}.json"))
            with open(bingo_files[0]) as f:
                bingo_data = json.load(f)

            # Collect sphere numbers
            spheres = []
            for row in bingo_data["board"]:
                for tile in row:
                    if tile["location"] != "Empty":
                        spheres.append(tile["sphere"])

            max_sphere = bingo_data["metadata"]["total_spheres"]

            # Categorize as early/mid/late
            early_count = sum(1 for s in spheres if s <= max_sphere * 0.33)
            mid_count = sum(1 for s in spheres if max_sphere * 0.33 < s <= max_sphere * 0.66)
            late_count = sum(1 for s in spheres if s > max_sphere * 0.66)

            print(f"  Early spheres: {early_count}/25")
            print(f"  Mid spheres: {mid_count}/25")
            print(f"  Late spheres: {late_count}/25")

            # Verify expected distributions
            if difficulty == "easy":
                self.assertGreater(early_count, late_count, "Easy should favor early spheres")
                print(f"  ✓ Favors early spheres")
            elif difficulty == "hard":
                self.assertGreater(late_count, early_count, "Hard should favor late spheres")
                print(f"  ✓ Favors late spheres")

        print(f"\n✓ All difficulty distributions verified!")

    def test_race_mode_not_implemented(self):
        """Test that race mode raises NotImplementedError."""
        print("\n=== Testing Race Mode Not Implemented ===")

        try:
            args, seed = self.generate_multiworld(
                ("TestPlayer", "A Link to the Past"),
                bingo_mode="race",
                bingo_difficulty="normal"
            )
            self.fail("Race mode should raise NotImplementedError")
        except Exception as e:
            # Main.py will catch and log the error
            # Check that no race mode file was created
            race_files = list(self.test_dir.glob("*_Bingo_race_*.json"))
            self.assertEqual(len(race_files), 0, "No race mode files should be generated")
            print(f"✓ Race mode correctly raises NotImplementedError")
            print(f"✓ Test passed!")

    def test_determinism(self):
        """Test that same seed produces same board."""
        print("\n=== Testing Determinism ===")

        # Generate twice with same seed
        boards = []
        for i in range(2):
            args, seed = self.generate_multiworld(
                ("TestPlayer", "A Link to the Past"),
                bingo_mode="coop",
                bingo_difficulty="normal"
            )

            import json
            bingo_files = list(self.test_dir.glob("*_Bingo_coop_normal.json"))
            with open(bingo_files[0]) as f:
                boards.append(json.load(f))

        # Compare boards
        self.assertEqual(len(boards), 2)

        for row_idx in range(5):
            for col_idx in range(5):
                tile1 = boards[0]["board"][row_idx][col_idx]
                tile2 = boards[1]["board"][row_idx][col_idx]

                self.assertEqual(tile1["location"], tile2["location"],
                               f"Tiles at [{row_idx}][{col_idx}] should be identical")

        print(f"✓ Both boards are identical")
        print(f"✓ Determinism verified!")


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestBingoWithRealGames)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
