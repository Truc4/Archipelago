#!/usr/bin/env python3
"""
Web tracker tests for Bingo co-op mode.

Tests that the web API correctly tracks location completion in real-time
and updates the bingo board for all players in co-op mode.
"""

import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from uuid import uuid4

# Add Archipelago to path
sys.path.insert(0, str(Path(__file__).parent))

# Import after path is set
from WebHostLib.api.bingo import (
    _process_bingo_board,
    _calculate_bingo_status,
    _validate_bingo_data,
)


class TestBingoWebTrackerCoopMode(unittest.TestCase):
    """Test web tracker for co-op mode bingo boards."""

    def setUp(self):
        """Set up test fixtures."""
        self.tracker_id = uuid4()

        # Create a sample co-op bingo board
        self.sample_coop_board = {
            "version": "1.0",
            "seed": 123456,
            "difficulty": "normal",
            "mode": "coop",
            "board": [
                [
                    {
                        "location": "Link's House (Player 1)",
                        "player": 1,
                        "game": "A Link to the Past",
                        "sphere": 1,
                        "item": "Lamp"
                    },
                    {
                        "location": "Deku Tree (Player 2)",
                        "player": 2,
                        "game": "Ocarina of Time",
                        "sphere": 2,
                        "item": "Kokiri Sword"
                    },
                    {
                        "location": "Morph Ball (Player 1)",
                        "player": 1,
                        "game": "A Link to the Past",
                        "sphere": 1,
                        "item": "Morph Ball"
                    },
                    {
                        "location": "Goron City (Player 2)",
                        "player": 2,
                        "game": "Ocarina of Time",
                        "sphere": 3,
                        "item": "Bombs"
                    },
                    {
                        "location": "Eastern Palace (Player 1)",
                        "player": 1,
                        "game": "A Link to the Past",
                        "sphere": 2,
                        "item": "Bow"
                    }
                ],
                [
                    {
                        "location": f"Location_{i} (Player {(i % 2) + 1})",
                        "player": (i % 2) + 1,
                        "game": "A Link to the Past" if i % 2 == 0 else "Ocarina of Time",
                        "sphere": (i % 5) + 1,
                        "item": f"Item_{i}"
                    }
                    for i in range(5, 10)
                ],
                [
                    {
                        "location": f"Location_{i} (Player {(i % 2) + 1})",
                        "player": (i % 2) + 1,
                        "game": "A Link to the Past" if i % 2 == 0 else "Ocarina of Time",
                        "sphere": (i % 5) + 1,
                        "item": f"Item_{i}"
                    }
                    for i in range(10, 15)
                ],
                [
                    {
                        "location": f"Location_{i} (Player {(i % 2) + 1})",
                        "player": (i % 2) + 1,
                        "game": "A Link to the Past" if i % 2 == 0 else "Ocarina of Time",
                        "sphere": (i % 5) + 1,
                        "item": f"Item_{i}"
                    }
                    for i in range(15, 20)
                ],
                [
                    {
                        "location": f"Location_{i} (Player {(i % 2) + 1})",
                        "player": (i % 2) + 1,
                        "game": "A Link to the Past" if i % 2 == 0 else "Ocarina of Time",
                        "sphere": (i % 5) + 1,
                        "item": f"Item_{i}"
                    }
                    for i in range(20, 25)
                ]
            ],
            "metadata": {
                "total_spheres": 10,
                "players": 2
            }
        }

    def test_validate_coop_board(self):
        """Test that co-op board passes validation."""
        print("\n=== Testing Co-op Board Validation ===")

        is_valid = _validate_bingo_data(self.sample_coop_board)
        self.assertTrue(is_valid, "Co-op board should be valid")

        print("✓ Co-op board structure is valid")

    def test_process_board_no_completions(self):
        """Test processing board when no locations are completed."""
        print("\n=== Testing Board Processing (No Completions) ===")

        # No checked locations
        checked_locations = {
            (0, 1): set(),  # Team 0, Player 1
            (0, 2): set(),  # Team 0, Player 2
        }

        location_name_maps = {
            "A Link to the Past": {},
            "Ocarina of Time": {},
        }

        processed_board = _process_bingo_board(
            self.sample_coop_board["board"],
            checked_locations,
            location_name_maps
        )

        # Verify no tiles are marked as completed
        for row in processed_board:
            for tile in row:
                self.assertFalse(tile["completed"], f"Tile {tile['location']} should not be completed")

        print("✓ No tiles marked as completed")
        print("✓ Test passed!")

    def test_process_board_player1_completions(self):
        """Test that Player 1's completed locations mark tiles correctly."""
        print("\n=== Testing Player 1 Location Completions ===")

        # Mock location IDs
        location_name_maps = {
            "A Link to the Past": {
                "Link's House": 1001,
                "Morph Ball": 1002,
                "Eastern Palace": 1003,
            },
            "Ocarina of Time": {},
        }

        # Player 1 has checked some locations
        checked_locations = {
            (0, 1): {1001, 1002},  # Link's House, Morph Ball
            (0, 2): set(),
        }

        processed_board = _process_bingo_board(
            self.sample_coop_board["board"],
            checked_locations,
            location_name_maps
        )

        # Verify first row
        self.assertTrue(processed_board[0][0]["completed"], "Link's House should be completed")
        self.assertFalse(processed_board[0][1]["completed"], "Deku Tree (P2) should not be completed")
        self.assertTrue(processed_board[0][2]["completed"], "Morph Ball should be completed")
        self.assertFalse(processed_board[0][3]["completed"], "Goron City (P2) should not be completed")
        self.assertFalse(processed_board[0][4]["completed"], "Eastern Palace not checked yet")

        print("✓ Player 1's checked locations correctly marked")
        print("✓ Player 2's locations remain unchecked")
        print("✓ Test passed!")

    def test_process_board_both_players_completions(self):
        """Test co-op mode: both players' completions update the shared board."""
        print("\n=== Testing Co-op Mode: Both Players Completing Locations ===")

        location_name_maps = {
            "A Link to the Past": {
                "Link's House": 1001,
                "Morph Ball": 1002,
                "Eastern Palace": 1003,
            },
            "Ocarina of Time": {
                "Deku Tree": 2001,
                "Goron City": 2002,
            },
        }

        # Both players have checked locations
        checked_locations = {
            (0, 1): {1001, 1002},  # Player 1: Link's House, Morph Ball
            (0, 2): {2001, 2002},  # Player 2: Deku Tree, Goron City
        }

        processed_board = _process_bingo_board(
            self.sample_coop_board["board"],
            checked_locations,
            location_name_maps
        )

        # Verify both players' completions are reflected
        self.assertTrue(processed_board[0][0]["completed"], "Link's House (P1) completed")
        self.assertTrue(processed_board[0][1]["completed"], "Deku Tree (P2) completed")
        self.assertTrue(processed_board[0][2]["completed"], "Morph Ball (P1) completed")
        self.assertTrue(processed_board[0][3]["completed"], "Goron City (P2) completed")

        completed_count = sum(1 for row in processed_board for tile in row if tile["completed"])
        print(f"✓ {completed_count} tiles marked as completed")
        print("✓ Both players' completions reflected on shared board")
        print("✓ Co-op mode tracking works correctly!")

    def test_calculate_bingo_status_no_lines(self):
        """Test status calculation with no completed lines."""
        print("\n=== Testing Bingo Status: No Lines ===")

        # Create board with scattered completions (no lines)
        board = []
        for row_idx in range(5):
            row = []
            for col_idx in range(5):
                row.append({
                    "location": f"Loc_{row_idx}_{col_idx}",
                    "player": 1,
                    "game": "Test",
                    "sphere": 1,
                    "item": "Item",
                    "location_id": row_idx * 5 + col_idx,
                    "completed": (row_idx + col_idx) % 3 == 0  # Scattered pattern
                })
            board.append(row)

        status = _calculate_bingo_status(board)

        self.assertEqual(status["total_tiles"], 25)
        self.assertGreater(status["completed_tiles"], 0)
        self.assertEqual(len(status["completed_lines"]), 0, "Should have no completed lines")

        print(f"✓ Completed tiles: {status['completed_tiles']}/25")
        print(f"✓ No completed lines detected")
        print("✓ Test passed!")

    def test_calculate_bingo_status_with_row(self):
        """Test status calculation with completed row."""
        print("\n=== Testing Bingo Status: Completed Row ===")

        # Create board with row 2 completed
        board = []
        for row_idx in range(5):
            row = []
            for col_idx in range(5):
                row.append({
                    "location": f"Loc_{row_idx}_{col_idx}",
                    "player": 1,
                    "game": "Test",
                    "sphere": 1,
                    "item": "Item",
                    "location_id": row_idx * 5 + col_idx,
                    "completed": row_idx == 2  # Row 2 completed
                })
            board.append(row)

        status = _calculate_bingo_status(board)

        self.assertEqual(status["completed_tiles"], 5)
        self.assertIn("row_2", status["completed_lines"])
        self.assertEqual(len(status["completed_lines"]), 1)

        print(f"✓ Completed tiles: {status['completed_tiles']}/25")
        print(f"✓ Detected completed lines: {status['completed_lines']}")
        print("✓ Test passed!")

    def test_calculate_bingo_status_with_column(self):
        """Test status calculation with completed column."""
        print("\n=== Testing Bingo Status: Completed Column ===")

        # Create board with column 3 completed
        board = []
        for row_idx in range(5):
            row = []
            for col_idx in range(5):
                row.append({
                    "location": f"Loc_{row_idx}_{col_idx}",
                    "player": 1,
                    "game": "Test",
                    "sphere": 1,
                    "item": "Item",
                    "location_id": row_idx * 5 + col_idx,
                    "completed": col_idx == 3  # Column 3 completed
                })
            board.append(row)

        status = _calculate_bingo_status(board)

        self.assertEqual(status["completed_tiles"], 5)
        self.assertIn("col_3", status["completed_lines"])
        self.assertEqual(len(status["completed_lines"]), 1)

        print(f"✓ Completed tiles: {status['completed_tiles']}/25")
        print(f"✓ Detected completed lines: {status['completed_lines']}")
        print("✓ Test passed!")

    def test_calculate_bingo_status_with_diagonal(self):
        """Test status calculation with completed diagonal."""
        print("\n=== Testing Bingo Status: Completed Diagonal ===")

        # Create board with main diagonal completed
        board = []
        for row_idx in range(5):
            row = []
            for col_idx in range(5):
                row.append({
                    "location": f"Loc_{row_idx}_{col_idx}",
                    "player": 1,
                    "game": "Test",
                    "sphere": 1,
                    "item": "Item",
                    "location_id": row_idx * 5 + col_idx,
                    "completed": row_idx == col_idx  # Main diagonal
                })
            board.append(row)

        status = _calculate_bingo_status(board)

        self.assertEqual(status["completed_tiles"], 5)
        self.assertIn("diag_main", status["completed_lines"])
        self.assertEqual(len(status["completed_lines"]), 1)

        print(f"✓ Completed tiles: {status['completed_tiles']}/25")
        print(f"✓ Detected completed lines: {status['completed_lines']}")
        print("✓ Test passed!")

    def test_calculate_bingo_status_multiple_lines(self):
        """Test status calculation with multiple completed lines."""
        print("\n=== Testing Bingo Status: Multiple Lines (BINGO!) ===")

        # Create board with row 0, column 4, and anti-diagonal completed
        board = []
        for row_idx in range(5):
            row = []
            for col_idx in range(5):
                completed = (
                    row_idx == 0 or  # Row 0
                    col_idx == 4 or  # Column 4
                    row_idx + col_idx == 4  # Anti-diagonal
                )
                row.append({
                    "location": f"Loc_{row_idx}_{col_idx}",
                    "player": 1,
                    "game": "Test",
                    "sphere": 1,
                    "item": "Item",
                    "location_id": row_idx * 5 + col_idx,
                    "completed": completed
                })
            board.append(row)

        status = _calculate_bingo_status(board)

        self.assertIn("row_0", status["completed_lines"])
        self.assertIn("col_4", status["completed_lines"])
        self.assertIn("diag_anti", status["completed_lines"])
        self.assertEqual(len(status["completed_lines"]), 3)

        print(f"✓ Completed tiles: {status['completed_tiles']}/25")
        print(f"✓ Detected completed lines: {status['completed_lines']}")
        print("✓ Multiple lines detected correctly!")
        print("🎉 BINGO!")

    def test_coop_mode_real_time_simulation(self):
        """Simulate real-time co-op gameplay where players progressively complete locations."""
        print("\n=== Simulating Real-Time Co-op Gameplay ===")

        location_name_maps = {
            "A Link to the Past": {
                "Link's House": 1001,
                "Morph Ball": 1002,
                "Eastern Palace": 1003,
            },
            "Ocarina of Time": {
                "Deku Tree": 2001,
                "Goron City": 2002,
            },
        }

        # Simulate progressive gameplay
        scenarios = [
            {
                "time": "Start",
                "checked": {(0, 1): set(), (0, 2): set()},
                "expected_completed": 0,
            },
            {
                "time": "5 minutes in: Player 1 finds Link's House",
                "checked": {(0, 1): {1001}, (0, 2): set()},
                "expected_completed": 1,
            },
            {
                "time": "10 minutes: Player 2 finds Deku Tree",
                "checked": {(0, 1): {1001}, (0, 2): {2001}},
                "expected_completed": 2,
            },
            {
                "time": "15 minutes: Player 1 finds Morph Ball",
                "checked": {(0, 1): {1001, 1002}, (0, 2): {2001}},
                "expected_completed": 3,
            },
            {
                "time": "20 minutes: Player 2 finds Goron City",
                "checked": {(0, 1): {1001, 1002}, (0, 2): {2001, 2002}},
                "expected_completed": 4,
            },
        ]

        for scenario in scenarios:
            print(f"\n  {scenario['time']}")

            processed_board = _process_bingo_board(
                self.sample_coop_board["board"],
                scenario["checked"],
                location_name_maps
            )

            status = _calculate_bingo_status(processed_board)

            self.assertEqual(
                status["completed_tiles"],
                scenario["expected_completed"],
                f"At '{scenario['time']}', should have {scenario['expected_completed']} tiles"
            )

            print(f"    Tiles completed: {status['completed_tiles']}/25 ({status['completion_percentage']:.1f}%)")

            if status["completed_lines"]:
                print(f"    🎉 Completed lines: {', '.join(status['completed_lines'])}")

        print("\n✓ Real-time co-op tracking simulation successful!")
        print("✓ Both players' progress tracked on shared board!")

    def test_coop_board_player_isolation(self):
        """Test that player 1 cannot complete player 2's locations (and vice versa)."""
        print("\n=== Testing Player Isolation (Players Can Only Complete Own Locations) ===")

        location_name_maps = {
            "A Link to the Past": {
                "Link's House": 1001,
            },
            "Ocarina of Time": {
                "Deku Tree": 2001,
            },
        }

        # Player 1 somehow "checks" Player 2's location (shouldn't happen in real game)
        # But we'll test that the system correctly associates locations with players
        checked_locations = {
            (0, 1): {2001},  # Player 1 checks location 2001 (which is Player 2's Deku Tree)
            (0, 2): set(),
        }

        processed_board = _process_bingo_board(
            self.sample_coop_board["board"],
            checked_locations,
            location_name_maps
        )

        # The Deku Tree tile (Player 2's location) should NOT be completed
        # because it was checked by Player 1, not Player 2
        deku_tree_tile = processed_board[0][1]  # Row 0, Col 1
        self.assertEqual(deku_tree_tile["player"], 2)
        self.assertFalse(
            deku_tree_tile["completed"],
            "Player 2's location should not be marked complete when Player 1 checks it"
        )

        print("✓ Player isolation verified")
        print("✓ Locations only count when checked by the correct player")
        print("✓ Test passed!")


def run_tests():
    """Run all web tracker tests."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestBingoWebTrackerCoopMode)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
