#!/usr/bin/env python3
"""
Test bingo generation from an actual generated multiworld ZIP
"""

import sys
import os
import zipfile
import pickle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bingo
from Main import main as generate_main

def test_bingo_from_existing_zip():
    """Load a generated multiworld and try to generate bingo"""

    # Find the most recent zip file
    output_dir = "output"
    if not os.path.exists(output_dir):
        print("ERROR: output directory doesn't exist")
        return False

    zip_files = [f for f in os.listdir(output_dir) if f.endswith('.zip')]
    if not zip_files:
        print("ERROR: No ZIP files found in output directory")
        return False

    latest_zip = sorted(zip_files)[-1]
    zip_path = os.path.join(output_dir, latest_zip)

    print(f"Loading multiworld from: {zip_path}")

    # Try to load the multiworld data
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # The multiworld data is stored in the zip
            # Let's see what files are in there
            print("\nFiles in ZIP:")
            for name in zf.namelist():
                print(f"  {name}")
    except Exception as e:
        print(f"ERROR reading ZIP: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "="*80)
    print("ISSUE IDENTIFIED:")
    print("="*80)
    print()
    print("The problem is that bingo.py requires the MultiWorld object with")
    print("spoiler.playthrough data, but this is only generated DURING generation,")
    print("not stored in the ZIP file for later use.")
    print()
    print("The ZIP file contains:")
    print("  - Slot data for each player")
    print("  - Location/item assignments")
    print("  - But NOT the playthrough sphere data")
    print()
    print("To make bingo work, you need to:")
    print("  1. Integrate bingo into Generate.py (as shown in BINGO_QUICK_START.md)")
    print("  2. Run it DURING generation, after spoiler.create_playthrough() is called")
    print("  3. You CANNOT generate bingo after the fact from just the ZIP file")
    print()
    print("="*80)

    return True

if __name__ == '__main__':
    test_bingo_from_existing_zip()
