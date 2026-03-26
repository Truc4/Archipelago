# Bingo Modes: Co-op vs Race

Archipelago Bingo supports two distinct gameplay modes to accommodate different play styles.

---

## Understanding the Problem

In Archipelago multiworld games:
- **Each player plays their own game** (e.g., Player 1 = ALTTP, Player 2 = OOT, Player 3 = SM)
- **Each player can only complete locations in their own game**
- Player 1 cannot complete Player 2's locations and vice versa

This means a single shared board needs careful design to work for all players.

---

## Mode 1: Co-op (IMPLEMENTED ✅)

### Concept
All players share **one board** with locations from all players mixed together. Each tile belongs to a specific player, and only that player can complete it. Players work together to fill the entire board.

### How It Works
```
╔════════════════════════════════════════════════════════════╗
║         SHARED BINGO BOARD (All Players)                  ║
╠════════════════════════════════════════════════════════════╣
║  ALTTP: Link's    │  OOT: Deku Tree  │  SM: Morph Ball   ║
║  House (P1) [S1]  │  (P2) [S2]       │  (P3) [S1]        ║
║───────────────────┼──────────────────┼───────────────────║
║  OOT: Goron City  │  ALTTP: Eastern  │  OOT: Forest      ║
║  (P2) [S3]        │  Palace (P1) [S2]│  Temple (P2) [S4] ║
║───────────────────┼──────────────────┼───────────────────║
║  SM: Brinstar     │  OOT: Fire Temple│  ALTTP: Desert    ║
║  (P3) [S5]        │  (P2) [S6]       │  Palace (P1) [S3] ║
╚════════════════════════════════════════════════════════════╝

When Player 1 finds "Link's House", that tile is marked for EVERYONE.
When Player 2 finds "Deku Tree", that tile is marked for EVERYONE.
Players coordinate to complete lines/patterns together.
```

### Fair Distribution
The system automatically ensures fair tile distribution:
- **Auto-calculated max_per_player**: `(25 ÷ num_players) + 3`
  - 2 players: max 15 tiles per player → possible distribution 15-10, 13-12
  - 3 players: max 11 tiles per player → possible distribution 11-8-6, 9-9-7
  - 4 players: max 9 tiles per player → possible distribution 9-8-5-3, 7-7-7-4

### Generation Example
```bash
# Generate co-op board with normal difficulty
python Generate.py --spoiler 3 --bingo coop:normal

# Or shorthand (coop is default)
python Generate.py --spoiler 3 --bingo normal

# Output file
AP_123456789_Bingo_coop_normal.json
```

### Gameplay
- **Objective**: Work together to complete bingo patterns (line, diagonal, blackout, etc.)
- **Communication**: Players coordinate who should prioritize which tiles
- **Strategy**: Balance progression needs with bingo goals
- **Victory**: Team wins when the agreed pattern is complete

### Pros
- ✅ Encourages teamwork and coordination
- ✅ Players with fewer locations still contribute meaningfully
- ✅ Single board is easy to track and display
- ✅ Works well for any number of players

### Cons
- ❌ Not competitive between players
- ❌ Requires communication/coordination
- ❌ Player with easy locations might finish their tiles quickly while others lag

---

## Mode 2: Race (NOT YET IMPLEMENTED ⚠️)

### Concept
Each player gets **their own separate board** containing only their own locations. Players race to complete their individual boards first.

### How It Would Work
```
╔═══════════════════════════════╗  ╔═══════════════════════════════╗  ╔═══════════════════════════════╗
║   PLAYER 1 BOARD (ALTTP)      ║  ║   PLAYER 2 BOARD (OOT)        ║  ║   PLAYER 3 BOARD (SM)         ║
╠═══════════════════════════════╣  ╠═══════════════════════════════╣  ╠═══════════════════════════════╣
║ Link's House │ Eastern Palace ║  ║ Deku Tree │ Goron City        ║  ║ Morph Ball │ Brinstar         ║
║ [S1]         │ [S2]           ║  ║ [S2]      │ [S3]              ║  ║ [S1]       │ [S5]             ║
║──────────────┼────────────────║  ║───────────┼───────────────────║  ║────────────┼──────────────────║
║ Desert Palace│ Tower of Hera  ║  ║ Forest    │ Fire Temple       ║  ║ Norfair    │ Maridia          ║
║ [S3]         │ [S4]           ║  ║ Temple[S4]│ [S6]              ║  ║ [S3]       │ [S7]             ║
╚═══════════════════════════════╝  ╚═══════════════════════════════╝  ╚═══════════════════════════════╝

Each player only sees/tracks their own board.
First to complete a bingo pattern on their board wins.
```

### Generation (When Implemented)
```bash
# Generate race boards with hard difficulty
python Generate.py --spoiler 3 --bingo race:hard

# Output files (one per player)
AP_123456789_Bingo_race_hard_P1.json
AP_123456789_Bingo_race_hard_P2.json
AP_123456789_Bingo_race_hard_P3.json
```

### Gameplay
- **Objective**: Be the first to complete a bingo pattern on your own board
- **Competition**: Direct race between players
- **Strategy**: Optimize your own routing, don't worry about others
- **Victory**: Individual player wins

### Pros
- ✅ Direct competition between players
- ✅ No need for coordination
- ✅ Each player has clear individual goals
- ✅ Better for racing/speedrunning

### Cons
- ❌ Requires each player has ≥25 locations (might not work for all games/settings)
- ❌ More complex tracking (N boards instead of 1)
- ❌ Harder to display/compare boards visually
- ❌ Players with easier games/seeds might have unfair advantage

---

## Implementation Status

### ✅ Co-op Mode (DONE)
- [x] Single shared board generation
- [x] Fair tile distribution across players
- [x] Auto-calculated max_per_player constraint
- [x] JSON output format
- [x] Text formatting for spoiler log
- [x] Command-line arguments
- [x] Integration with Main.py and Generate.py

### ⚠️ Race Mode (TODO)

See detailed TODOs in `bingo.py::_generate_race_boards()` function.

#### Required Implementation Tasks

**1. Candidate Filtering by Player**
```python
# For each player, filter to only their locations
for player in range(1, multiworld.players + 1):
    player_candidates = [(loc, sphere) for loc, sphere in candidates if loc.player == player]
```

**2. Validation**
```python
# Check if player has enough locations for a board
if len(player_candidates) < 25:
    # Options:
    # A) Raise error: "Player N has only X locations (need 25)"
    # B) Generate smaller board (3x3 = 9 tiles, 4x4 = 16 tiles)
    # C) Fill remaining tiles with dummy/impossible locations
    # D) Allow duplicate locations with different items?
```

**3. Per-Player Board Generation**
```python
# Generate separate board for each player
boards = {}
for player in range(1, multiworld.players + 1):
    # Use player-specific seed for variety
    seed = _derive_bingo_seed(multiworld.seed + player, difficulty)

    # Generate board using only this player's locations
    board_data = generate_board_for_player(
        multiworld, player, player_candidates[player],
        difficulty, seed
    )
    boards[player] = board_data
```

**4. Output Format Design Decision**

**Option A: Multiple JSON files**
```
AP_123456789_Bingo_race_hard_P1.json
AP_123456789_Bingo_race_hard_P2.json
AP_123456789_Bingo_race_hard_P3.json
```
- Pros: Easy to distribute individual files to players
- Cons: More files to manage

**Option B: Single JSON with nested structure**
```json
{
  "version": "1.0",
  "seed": 123456789,
  "mode": "race",
  "difficulty": "hard",
  "boards": {
    "1": { "board": [[...]], "player_name": "Alice", "game": "ALTTP" },
    "2": { "board": [[...]], "player_name": "Bob", "game": "OOT" },
    "3": { "board": [[...]], "player_name": "Charlie", "game": "SM" }
  }
}
```
- Pros: Single file, easier to track
- Cons: Larger file, need to filter for individual player view

**5. Text Formatting**

**Option A: Separate sections in spoiler**
```
================================================================================
BINGO BOARDS - Mode: RACE - Difficulty: HARD
================================================================================

PLAYER 1 (Alice - A Link to the Past):
Link's House [S1]     | Eastern Palace [S2]  | Desert Palace [S3]
Tower of Hera [S4]    | ...

PLAYER 2 (Bob - Ocarina of Time):
Deku Tree [S2]        | Goron City [S3]      | Forest Temple [S4]
...
```

**Option B: Side-by-side comparison**
```
================================================================================
         Player 1 (ALTTP)    |    Player 2 (OOT)     |    Player 3 (SM)
================================================================================
Row 1:   Link's House [S1]   |   Deku Tree [S2]      |   Morph Ball [S1]
Row 2:   Eastern Palace [S2] |   Goron City [S3]     |   Brinstar [S5]
...
```

**6. Web Tracker Updates**

Update `WebHostLib/templates/bingo_tracker.html` to:
- Detect race mode vs coop mode
- Show player-specific board for race mode
- Add player selector dropdown: "View Player: [1] [2] [3]"
- OR: Show all boards in tabs/accordion

**7. Edge Cases to Handle**

| Case | Solution |
|------|----------|
| Single player game | Race mode doesn't make sense → auto-fallback to coop mode |
| Player has < 25 locations | Error with helpful message, or generate smaller board (3x3, 4x4) |
| Very uneven location counts | P1=100 locs, P2=30 locs → Still works, but may affect fairness/difficulty |
| 10+ players | Need to generate 10+ separate boards → may be slow, consider optimization |
| Event locations | Already filtered out in `_extract_location_candidates` |

**8. Determinism Considerations**

```python
# Each player's board should be deterministic but different
# Option 1: Add player number to seed
seed_p1 = _derive_bingo_seed(multiworld.seed + 1, difficulty)
seed_p2 = _derive_bingo_seed(multiworld.seed + 2, difficulty)

# Option 2: Use player name hash
seed_pN = _derive_bingo_seed(multiworld.seed + hash(player_name), difficulty)

# Option 3: Use combination
seed_pN = _derive_bingo_seed(multiworld.seed, f"{difficulty}_player{N}")
```

**9. Main.py Integration**

Update the bingo generation block to handle race mode output:
```python
if args.bingo_mode == 'race':
    # board_data is a dict of {player: board_data}
    for player, player_board in board_data.items():
        filename = f'{outfilebase}_Bingo_race_{args.bingo_difficulty}_P{player}.json'
        bingo_path = os.path.join(temp_dir, filename)
        bingo.write_bingo_board_json(player_board, bingo_path)

    # Format all boards for spoiler
    if args.spoiler:
        spoiler_path = os.path.join(temp_dir, f'{outfilebase}_Spoiler.txt')
        with open(spoiler_path, 'a', encoding='utf-8') as f:
            f.write(bingo.format_race_boards_text(board_data))
else:
    # Existing coop mode logic
    ...
```

**10. Testing Requirements**

Before merging race mode:
- [ ] Test with 2 players (different games)
- [ ] Test with 4+ players
- [ ] Test with single player (should fallback to coop or error gracefully)
- [ ] Test with player having < 25 locations
- [ ] Test determinism (same seed = same boards)
- [ ] Test with very deep sphere counts (30+)
- [ ] Verify JSON format is valid and parseable
- [ ] Verify spoiler text formatting is readable

---

## Choosing a Mode

### Use Co-op Mode When:
- Playing casually with friends
- Want to encourage teamwork
- Have players with different skill levels
- Have players with games of varying location counts
- Want simple single-board tracking

### Use Race Mode When:
- Competitive racing/speedrunning
- All players want individual challenges
- Direct competition between players
- Each player has sufficient locations (≥25)
- Want to avoid coordination overhead

---

## Current Recommendation

**For now, use Co-op mode** (the only implemented mode). It works well for most use cases and is robust across different player counts and game types.

Race mode will be added in a future update once the implementation details above are addressed.

---

## Example Commands

```bash
# Co-op mode (default) - normal difficulty
python Generate.py --spoiler 3 --bingo normal

# Co-op mode - explicit
python Generate.py --spoiler 3 --bingo coop:hard

# Race mode - will fail with NotImplementedError until implemented
python Generate.py --spoiler 3 --bingo race:easy
# Error: "Race mode is not yet implemented. Use mode='coop' instead."
```

---

## Questions?

See also:
- `BINGO_SUMMARY.md` - Overall architecture and design
- `BINGO_INTEGRATION.md` - Integration guide
- `bingo.py::_generate_race_boards()` - Detailed implementation TODOs
