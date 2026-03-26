# Bingo Modes Implementation - Changelog

## Summary

Implemented **Co-op mode** for bingo boards and added framework for **Race mode** (to be implemented later).

The key insight: In Archipelago, each player plays their own game and can only complete their own locations. This requires two distinct bingo modes:
- **Co-op**: Shared board where players work together
- **Race**: Individual boards where players compete

---

## What Changed

### 1. Core Implementation (`bingo.py`)

#### Added Mode Parameter
```python
def generate_bingo_board(
    multiworld: MultiWorld,
    difficulty: str = "normal",
    mode: str = "coop",  # NEW: "coop" or "race"
    max_per_player: Optional[int] = None,
    max_per_sphere: Optional[int] = None,
) -> Dict:
```

#### Split into Two Functions

**`_generate_coop_board()`** ✅ IMPLEMENTED
- Generates one shared board with locations from all players
- Auto-calculates `max_per_player` for fair distribution:
  - Formula: `(25 ÷ num_players) + 3`
  - 2 players: max 15 tiles per player
  - 4 players: max 9 tiles per player
- Each tile belongs to a specific player
- Players work together to complete the board

**`_generate_race_boards()`** ⚠️ TODO
- Would generate N separate boards (one per player)
- Each board contains only that player's locations
- Players race to complete their individual boards
- Currently raises `NotImplementedError` with detailed TODOs

#### Updated Board Metadata
```json
{
  "version": "1.0",
  "mode": "coop",  // NEW FIELD
  "difficulty": "normal",
  "board": [[...]],
  ...
}
```

#### Updated Text Output
```
BINGO BOARD - Mode: COOP - Difficulty: NORMAL
```

---

### 2. Command-Line Arguments (`Generate.py`)

#### Updated `--bingo` Argument

**Old Format:**
```bash
python Generate.py --bingo normal
# Only accepted: easy, normal, hard
```

**New Format:**
```bash
# Just difficulty (defaults to coop)
python Generate.py --bingo normal

# Explicit mode:difficulty
python Generate.py --bingo coop:hard
python Generate.py --bingo race:easy
```

#### Parsing Logic
```python
if ':' in args.bingo:
    args.bingo_mode, args.bingo_difficulty = args.bingo.split(':', 1)
else:
    args.bingo_mode = 'coop'  # default
    args.bingo_difficulty = args.bingo

# Validation
if args.bingo_mode not in ['coop', 'race']:
    error(...)
if args.bingo_difficulty not in ['easy', 'normal', 'hard']:
    error(...)
```

---

### 3. Integration (`Main.py`)

#### Updated Bingo Generation Call
```python
# OLD
board_data = bingo.generate_bingo_board(multiworld, args.bingo)
bingo_path = f'{outfilebase}_Bingo_{args.bingo}.json'

# NEW
board_data = bingo.generate_bingo_board(
    multiworld,
    difficulty=args.bingo_difficulty,
    mode=args.bingo_mode
)
bingo_path = f'{outfilebase}_Bingo_{args.bingo_mode}_{args.bingo_difficulty}.json'
```

#### Output Filename Change
```
# OLD
AP_123456789_Bingo_normal.json

# NEW
AP_123456789_Bingo_coop_normal.json
AP_123456789_Bingo_race_hard.json  (when implemented)
```

---

### 4. Documentation

#### New File: `BINGO_MODES.md`
Comprehensive guide explaining:
- The problem (each player can only complete their own locations)
- Co-op mode (implemented)
- Race mode (not yet implemented)
- Detailed TODOs for race mode implementation
- Comparison table
- Use case recommendations

#### Updated Files
- `README_BINGO.md`: Added mode information, updated examples
- `BINGO_SUMMARY.md`: References new modes (if updated)
- `BINGO_USAGE_GUIDE.md`: Updated command examples (if needed)

---

## Testing Results

### Argument Parsing ✅
```
✓ --bingo normal            → mode=coop, difficulty=normal
✓ --bingo hard              → mode=coop, difficulty=hard
✓ --bingo coop:easy         → mode=coop, difficulty=easy
✓ --bingo race:hard         → mode=race, difficulty=hard

✓ --bingo invalid           → Correctly rejected
✓ --bingo coop:invalid      → Correctly rejected
✓ --bingo invalid:normal    → Correctly rejected
```

### Co-op Mode ✅
- Generates single shared board
- Fair tile distribution across players
- Deterministic output
- JSON and text formatting work correctly

### Race Mode ⚠️
- Correctly raises `NotImplementedError`
- Error message directs users to co-op mode
- Detailed TODOs in docstring

---

## Backwards Compatibility

### Command-Line Interface
**BREAKING CHANGE**: Output filename format changed

**Migration:**
```bash
# Old command still works (defaults to coop)
python Generate.py --spoiler 3 --bingo normal

# But output filename changed:
# OLD: AP_123456789_Bingo_normal.json
# NEW: AP_123456789_Bingo_coop_normal.json
```

**If you have scripts/tools that parse bingo filenames, update them:**
```bash
# OLD pattern
AP_*_Bingo_*.json

# NEW pattern
AP_*_Bingo_*_*.json
# OR: AP_*_Bingo_{coop,race}_*.json
```

### JSON Format
**BACKWARDS COMPATIBLE** - added new field:
```json
{
  "mode": "coop"  // NEW FIELD (optional for old parsers)
}
```

Old parsers can ignore this field. New parsers should read it.

---

## Race Mode Implementation TODO

See detailed implementation guide in `BINGO_MODES.md` and docstring in `bingo.py::_generate_race_boards()`.

### High-Level Tasks

1. **Candidate Filtering** - Filter locations by player
2. **Validation** - Handle players with < 25 locations
3. **Per-Player Generation** - Generate N boards with player-specific seeds
4. **Output Format** - Decide: multiple JSON files or nested structure?
5. **Text Formatting** - Format all boards for spoiler log
6. **Main.py Updates** - Handle multiple board outputs
7. **Web Tracker** - Update HTML tracker to support race mode
8. **Edge Cases** - Single player, uneven location counts, etc.
9. **Testing** - Comprehensive tests with various player counts
10. **Documentation** - Update all guides with race mode examples

### Estimated Effort
- Core implementation: 2-3 hours
- Testing: 1-2 hours
- Documentation: 1 hour
- **Total: ~5 hours**

---

## Current Status

### ✅ Co-op Mode (COMPLETE)
- [x] Core implementation
- [x] Argument parsing
- [x] Main.py integration
- [x] Fair tile distribution
- [x] JSON output
- [x] Text formatting
- [x] Documentation
- [x] Testing

### ⚠️ Race Mode (TODO)
- [ ] Core implementation
- [ ] Per-player board generation
- [ ] Output format (multiple files vs nested)
- [ ] Text formatting (multiple boards)
- [ ] Main.py integration updates
- [ ] Web tracker updates
- [ ] Edge case handling
- [ ] Testing
- [ ] Documentation updates

---

## Usage Examples

### Co-op Mode (Current)
```bash
# Generate co-op board (default)
python Generate.py --spoiler 3 --bingo normal

# Explicit co-op mode
python Generate.py --spoiler 3 --bingo coop:hard

# Output
AP_123456789_Bingo_coop_normal.json
AP_123456789_Spoiler.txt  (includes board at end)
```

### Race Mode (Future)
```bash
# Will work after implementation
python Generate.py --spoiler 3 --bingo race:easy

# Expected output
AP_123456789_Bingo_race_easy_P1.json
AP_123456789_Bingo_race_easy_P2.json
AP_123456789_Bingo_race_easy_P3.json
AP_123456789_Spoiler.txt  (includes all boards)
```

---

## Files Modified

### Core Implementation
- `bingo.py` - Added mode parameter, split into coop/race functions
- `Generate.py` - Updated argument parsing, added mode/difficulty split
- `Main.py` - Updated bingo generation call, changed output filename

### Documentation
- `BINGO_MODES.md` - **NEW** - Comprehensive modes guide
- `BINGO_MODES_CHANGELOG.md` - **NEW** - This file
- `README_BINGO.md` - Updated with mode information
- (Other docs may need updates)

### Not Modified (Yet)
- `test_bingo*.py` - Should add tests for race mode when implemented
- `WebHostLib/templates/bingo_tracker.html` - Needs race mode support
- `WebHostLib/api/bingo.py` - May need updates for race mode

---

## Migration Guide

### For Users
No action needed! Old commands work the same:
```bash
# This still works
python Generate.py --spoiler 3 --bingo normal
```

Just note the output filename changed:
- Old: `AP_123456789_Bingo_normal.json`
- New: `AP_123456789_Bingo_coop_normal.json`

### For Developers
If you parse bingo JSON files:
```python
# OLD
board = json.load(f)
difficulty = board['difficulty']

# NEW (backwards compatible)
board = json.load(f)
difficulty = board['difficulty']
mode = board.get('mode', 'coop')  # Default to 'coop' for old files
```

If you parse bingo filenames:
```python
# OLD regex
pattern = r'AP_(\d+)_Bingo_(\w+)\.json'
# Captures: seed, difficulty

# NEW regex
pattern = r'AP_(\d+)_Bingo_(\w+)_(\w+)\.json'
# Captures: seed, mode, difficulty
```

---

## Questions & Answers

### Q: Why split into two modes?
**A:** In Archipelago, Player 1 can only complete Player 1's locations. A single board must either be shared (co-op) or individual (race) to make sense.

### Q: Can I use the old `--bingo normal` format?
**A:** Yes! It defaults to co-op mode. The full format is `--bingo coop:normal`.

### Q: When will race mode be implemented?
**A:** When someone has time! See TODOs in `BINGO_MODES.md` and `bingo.py::_generate_race_boards()`. Estimated ~5 hours of work.

### Q: What if I try to use race mode now?
**A:** You'll get a `NotImplementedError` with a helpful message directing you to use co-op mode.

### Q: Does co-op mode ensure fair distribution?
**A:** Yes! It auto-calculates `max_per_player` to prevent one player from dominating the board.

### Q: Can I still customize max_per_player?
**A:** Yes, pass it explicitly to `generate_bingo_board()` in code, or it will auto-calculate.

---

## Rollback Instructions

If you need to revert these changes:

1. **Revert bingo.py:**
   ```bash
   git diff HEAD~1 bingo.py  # Review changes
   git checkout HEAD~1 -- bingo.py
   ```

2. **Revert Generate.py:**
   ```bash
   git checkout HEAD~1 -- Generate.py
   ```

3. **Revert Main.py:**
   ```bash
   git checkout HEAD~1 -- Main.py
   ```

4. **Remove new docs:**
   ```bash
   rm BINGO_MODES.md BINGO_MODES_CHANGELOG.md
   ```

---

## Contact & Feedback

For questions, issues, or to contribute race mode implementation:
- See `BINGO_MODES.md` for detailed implementation guide
- Check `bingo.py::_generate_race_boards()` for code TODOs
- Refer to `README_BINGO.md` for general usage

---

**Status:** Co-op mode ready for production use! 🎉
**Next Steps:** Implement race mode when needed. 🏁
