# Bingo Module Integration Guide

**Note:** The bingo feature has been integrated into Generate.py and Main.py. This document explains how the integration works and is provided for reference and understanding.

This document explains how to integrate the Bingo board generator into Archipelago.

## Overview

The Bingo module (`bingo.py`) generates deterministic 5×5 bingo boards using playthrough sphere data. It works with any Archipelago game without requiring per-world modifications.

## Module Design

### Core Principle
- **Tiles are locations/checks**, not custom goals
- **Difficulty is based on sphere depth** (when locations become accessible)
- **Deterministic**: same seed + difficulty = same board
- **Generic**: no game-specific logic

### Difficulty Model
- **Easy**: Weighted toward early spheres (5.0 : 2.0 : 0.5)
- **Normal**: Weighted toward mid spheres (1.5 : 3.0 : 1.5)
- **Hard**: Weighted toward late spheres (0.5 : 2.0 : 5.0)

## Integration Steps

### 1. Add Command-Line Argument

In `Generate.py`, add the bingo difficulty argument:

```python
# Around line 40, after --spoiler argument
parser.add_argument('--bingo', type=str, default=None, choices=['easy', 'normal', 'hard'],
                    help='Generate a bingo board with specified difficulty')
```

### 2. Hook into Main.py

Add bingo generation calls right after `create_playthrough()` calls. There are **two locations**:

#### Location 1: Spoiler-only mode (around line 223)

```python
if args.spoiler_only:
    if args.spoiler > 1:
        logger.info('Calculating playthrough.')
        multiworld.spoiler.create_playthrough(create_paths=args.spoiler > 2)

    # >>> ADD BINGO GENERATION HERE <<<
    if args.bingo:
        import bingo
        try:
            board_data = bingo.generate_bingo_board(multiworld, args.bingo)
            bingo_path = output_path(f'{outfilebase}_Bingo_{args.bingo}.json')
            bingo.write_bingo_board_json(board_data, bingo_path)

            # Optionally append to spoiler
            if args.spoiler:
                with open(output_path(f'{outfilebase}_Spoiler.txt'), 'a', encoding='utf-8') as f:
                    f.write(bingo.format_bingo_board_text(board_data))
        except Exception as e:
            logger.error(f'Bingo generation failed: {e}')
    # >>> END BINGO GENERATION <<<

    multiworld.spoiler.to_file(output_path('%s_Spoiler.txt' % outfilebase))
    logger.info('Done. Skipped multidata modification. Total time: %s', time.perf_counter() - start)
    return multiworld
```

#### Location 2: Normal generation mode (around line 374)

```python
if args.spoiler > 1:
    logger.info('Calculating playthrough.')
    multiworld.spoiler.create_playthrough(create_paths=args.spoiler > 2)

# >>> ADD BINGO GENERATION HERE <<<
if args.bingo and args.spoiler > 1:  # Note: requires spoiler > 1 for playthrough
    import bingo
    try:
        board_data = bingo.generate_bingo_board(multiworld, args.bingo)
        bingo_path = os.path.join(temp_dir, f'{outfilebase}_Bingo_{args.bingo}.json')
        bingo.write_bingo_board_json(board_data, bingo_path)

        # Optionally append to spoiler
        if args.spoiler:
            with open(os.path.join(temp_dir, f'{outfilebase}_Spoiler.txt'), 'a', encoding='utf-8') as f:
                f.write(bingo.format_bingo_board_text(board_data))
    except Exception as e:
        logger.error(f'Bingo generation failed: {e}')
# >>> END BINGO GENERATION <<<

if args.spoiler:
    multiworld.spoiler.to_file(os.path.join(temp_dir, '%s_Spoiler.txt' % outfilebase))
```

### 3. Optional: Default Settings

If you want bingo enabled by default, modify the argument default:

```python
parser.add_argument('--bingo', type=str, default='normal', choices=['easy', 'normal', 'hard'],
                    help='Generate a bingo board with specified difficulty (default: normal)')
```

## Usage Examples

### Generate with Bingo

```bash
# Generate with normal difficulty bingo
python Generate.py --spoiler 3 --bingo normal

# Generate with hard difficulty bingo
python Generate.py --spoiler 3 --bingo hard

# Skip bingo generation
python Generate.py --spoiler 3
```

### Output Files

When `--bingo` is used, you'll get:
- `AP_12345_Bingo_normal.json` - Machine-readable board data
- `AP_12345_Spoiler.txt` - Includes bingo board section (if --spoiler is enabled)

## JSON Board Format

```json
{
  "version": "1.0",
  "seed": 123456789,
  "difficulty": "normal",
  "board": [
    [
      {
        "location": "Deku Tree Boss Key Chest (Player 1)",
        "player": 1,
        "game": "Ocarina of Time",
        "sphere": 3,
        "item": "Boss Key (Deku Tree)"
      },
      ...
    ],
    ...
  ],
  "metadata": {
    "total_spheres": 15,
    "players": 2
  }
}
```

## Optional Constraints

You can add constraints to the board generation:

```python
board_data = bingo.generate_bingo_board(
    multiworld,
    args.bingo,
    max_per_player=8,   # Max 8 tiles per player
    max_per_sphere=5    # Max 5 tiles per sphere
)
```

## Testing

### Quick Test

```bash
# Create a simple YAML
cat > test_player.yaml << EOF
name: TestPlayer
game: A Link to the Past
A Link to the Past:
  progression_balancing: 50
EOF

# Generate with bingo
python Generate.py --player_files_path . --spoiler 3 --bingo normal
```

### Verify Output

1. Check for `AP_*_Bingo_normal.json` in output directory
2. Open `AP_*_Spoiler.txt` and look for the bingo board section at the end
3. Verify determinism: same seed + difficulty = same board

## Architecture Notes

### Hook Point Rationale

The bingo generator must run **after** `create_playthrough()` because it needs the `collection_spheres` data. It should run **before** `to_file()` if you want to append the board to the spoiler text.

### Why This Design Works

1. **No per-world changes**: Uses existing `Location` and `Item` base classes
2. **Deterministic**: Uses `multiworld.seed` + difficulty hash for RNG seed
3. **Sphere-based difficulty**: Works for any game that computes spheres
4. **Constraint-friendly**: Easy to add caps per player/sphere without game logic

### What's NOT Included

- ❌ Custom goal parsing (e.g., "Kill 10 bosses")
- ❌ Game-specific difficulty scaling
- ❌ Bingo tracking/completion checking (client-side feature)
- ❌ Win condition enforcement

These would require per-world modifications, which violates the core design constraint.

## Advanced: Adding Bingo Options to Settings

If you want players to configure bingo through their YAML files, you can add a global option:

```python
# In Options.py or a suitable location
class BingoDifficulty(Choice):
    """Difficulty setting for Bingo board generation"""
    display_name = "Bingo Difficulty"
    option_off = 0
    option_easy = 1
    option_normal = 2
    option_hard = 3
    default = 0  # Off by default
```

Then access it in `Main.py` via player options.

## Troubleshooting

### "Not enough locations" error
- The game has fewer than 25 reachable locations in the playthrough
- Solution: Only generate bingo for seeds with sufficient locations

### "Bingo generation requires spoiler playthrough"
- You forgot to call `create_playthrough()` first
- Or `--spoiler` level is < 2

### Board has duplicate locations
- This should never happen due to the uniqueness constraint
- File a bug report with seed number

### Weights seem wrong
- Check `DIFFICULTY_PROFILES` in `bingo.py`
- Verify sphere distribution: `collection_spheres` should span early to late game

## Future Enhancements (Optional)

1. **Custom constraints**: Allow YAML configuration for max_per_player, max_per_sphere
2. **Visual board**: Generate HTML/PNG board representation
3. **Multiple boards**: Generate multiple boards per seed for variety
4. **Blacklist locations**: Allow worlds to mark locations unsuitable for bingo
5. **Item-based tiles**: Include "collect item X" tiles alongside location tiles

All of these can be added without breaking the core design principles.
