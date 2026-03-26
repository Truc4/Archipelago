# Bingo Board Usage & Hosting Guide

This guide covers the practical aspects of using bingo boards: where files are saved, how to host games, and how to track bingo during gameplay.

---

## 📂 Where Are Bingo Boards Saved?

### Default Output Location
By default, all generated files go to the **`output/`** directory in your Archipelago folder:

```
/home/curt/Code/Archipelago/output/
├── AP_<seed>_<seed_name>.zip          # Main multiworld data
├── AP_<seed>_Bingo_normal.json        # Bingo board (if --bingo used)
├── AP_<seed>_Spoiler.txt              # Spoiler log (if --spoiler used)
└── (other player-specific files)
```

### Custom Output Location
You can specify a different directory:

```bash
# Save to custom directory
python Generate.py --outputpath ~/my_archipelago_games --spoiler 3 --bingo normal

# Or use absolute path
python Generate.py --outputpath /tmp/archipelago_output --spoiler 3 --bingo normal
```

### File Naming Convention
```
AP_123456789_MySeedName_Bingo_normal.json    # Bingo board
AP_123456789_MySeedName_Spoiler.txt          # Spoiler (includes bingo at end)
AP_123456789_MySeedName.zip                  # Multiworld data
```

The seed number (e.g., `123456789`) ensures unique filenames.

---

## 🎮 How to Host an Archipelago Game

### Method 1: Generate and Host Locally (Recommended for Testing)

#### Step 1: Create a YAML file for each player
```yaml
# player1.yaml
name: Player1
game: A Link to the Past

A Link to the Past:
  progression_balancing: 50
  # ... other options
```

#### Step 2: Generate the multiworld
```bash
# From Archipelago directory
python Generate.py --player_files_path /path/to/yaml/files --spoiler 3 --bingo normal
```

**Output:**
```
INFO - Archipelago Version 0.5.1  -  Seed: 123456789
INFO - Found 2 World Types:
...
INFO - Done. Total Time: 5.2 seconds

Output files:
  output/AP_123456789.zip
  output/AP_123456789_Bingo_normal.json
  output/AP_123456789_Spoiler.txt
```

#### Step 3: Start the server
```bash
# Host the multiworld
python MultiServer.py output/AP_123456789.zip

# Or specify port
python MultiServer.py output/AP_123456789.zip --port 38281
```

**Server output:**
```
INFO - Loaded Archipelago multidata for seed 123456789
INFO - Hosting game on port 38281
INFO - Players: Player1, Player2
INFO - Server ready. Players may connect.
```

#### Step 4: Connect clients
Players use their game-specific clients:
- **ALTTP**: Use SNIClient.py or BizHawk
- **OOT**: Use OoTClient.py
- **Other games**: Check game-specific docs in `worlds/<game>/docs/`

```bash
# Example: Connect ALTTP client
python SNIClient.py

# In client:
/connect localhost:38281
```

---

### Method 2: Use Web Host (Easy for Remote Play)

#### Option A: Self-Host Web Interface
```bash
# Install dependencies
pip install flask

# Run web host
python WebHost.py

# Access at http://localhost:5000
```

Upload your YAML files through the web interface and generate.

---

### Method 3: Host on a Dedicated Server

#### Using Docker (Recommended)
```bash
# Generate first, then host
docker run -d \
  -v /path/to/output:/app/output \
  -p 38281:38281 \
  archipelago/server \
  python MultiServer.py /app/output/AP_123456789.zip
```

#### Direct on Linux Server
```bash
# SSH into server
ssh user@yourserver.com

# Install Archipelago
git clone https://github.com/ArchipelagoMW/Archipelago.git
cd Archipelago
pip install -r requirements.txt

# Generate (upload YAML files first)
python Generate.py --player_files_path ./yamls --spoiler 3 --bingo normal

# Host with screen (so it persists after logout)
screen -S archipelago
python MultiServer.py output/AP_123456789.zip --port 38281

# Detach: Ctrl+A, D
# Reattach: screen -r archipelago
```

---

## 📊 Using the Bingo Board During Gameplay

### The Problem: No Built-In Tracking

**Important:** The bingo module generates the board, but **does NOT track completion** during gameplay. Archipelago's core doesn't have bingo UI/tracking built-in.

You need to track bingo manually or use external tools.

---

### Solution 1: Manual Tracking with JSON File

#### Open the Bingo JSON
```bash
# Find your bingo file
cd output
cat AP_123456789_Bingo_normal.json
```

#### Example JSON:
```json
{
  "version": "1.0",
  "seed": 123456789,
  "difficulty": "normal",
  "board": [
    [
      {
        "location": "Link's House (Player 1)",
        "player": 1,
        "game": "A Link to the Past",
        "sphere": 1,
        "item": "Lamp"
      },
      ...
    ]
  ]
}
```

#### Track Manually
- **Print the board** or view in a text editor
- **Check off locations** as you complete them in-game
- **Use spreadsheet** (import JSON, mark cells)

---

### Solution 2: View Spoiler Text (Easy)

The spoiler file includes a formatted bingo board at the end:

```bash
# View the spoiler (SPOILER WARNING!)
cat output/AP_123456789_Spoiler.txt | tail -50
```

**Example Output:**
```
================================================================================
BINGO BOARD - Difficulty: NORMAL
================================================================================

Link's House [S1]       | Eastern Palace [S2]    | Desert Palace [S3]
Hyrule Castle [S1]      | Tower of Hera [S4]     | Swamp Palace [S5]
Thieves Town [S7]       | Ice Palace [S6]        | Skull Woods [S6]
Turtle Rock [S8]        | Ganons Tower [S9]      | Pyramid [S5]
Final Boss [S10]        | Triforce [S10]         | Sanctuary [S2]

================================================================================
Legend: [SN] = Sphere N (progression depth)
================================================================================
```

**How to track:**
1. Print this page or open in a text editor
2. Cross off locations as you find them
3. Mark rows/columns/diagonals as they complete

---

### Solution 3: Create a Web Tracker (Advanced)

You can build a simple HTML tracker:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Archipelago Bingo</title>
    <style>
        table { border-collapse: collapse; }
        td {
            border: 2px solid black;
            width: 150px;
            height: 100px;
            text-align: center;
            cursor: pointer;
            vertical-align: middle;
            padding: 5px;
        }
        td.checked {
            background-color: #90EE90;
            text-decoration: line-through;
        }
        .sphere { color: #666; font-size: 0.8em; }
    </style>
</head>
<body>
    <h1>Bingo Board - Seed: <span id="seed"></span></h1>
    <table id="bingo-board"></table>

    <script>
        // Load your bingo JSON
        const bingoData = {
            /* Paste your JSON here or load from file */
        };

        document.getElementById('seed').textContent = bingoData.seed;

        const board = document.getElementById('bingo-board');
        bingoData.board.forEach(row => {
            const tr = document.createElement('tr');
            row.forEach(tile => {
                const td = document.createElement('td');
                td.innerHTML = `
                    ${tile.location}<br>
                    <span class="sphere">[S${tile.sphere}]</span>
                `;
                td.onclick = () => td.classList.toggle('checked');
                tr.appendChild(td);
            });
            board.appendChild(tr);
        });
    </script>
</body>
</html>
```

**Usage:**
1. Save as `bingo_tracker.html`
2. Paste your JSON into the script
3. Open in browser
4. Click tiles to check them off

---

### Solution 4: Use OBS Overlay (Streaming)

For streamers:

1. **Create HTML tracker** (from Solution 3)
2. **Add Browser Source in OBS**:
   - Source → Browser
   - URL: `file:///path/to/bingo_tracker.html`
   - Width: 800, Height: 600
3. **Position overlay** on stream

---

### Solution 5: External Bingo Tools

Use existing bingo tools (not Archipelago-specific):

- **Bingosync** (https://bingosync.com/)
  - Create custom board
  - Manually enter locations from JSON
  - Sync with other players

- **Google Sheets**
  - Import JSON data
  - Share with players
  - Mark cells as complete

---

## 🔍 Checking Locations In-Game

### How Do I Know When I've Found a Location?

**In the Archipelago Client:**
- Locations are automatically sent to the server when found
- Check the client log or `/received` command

**In the Spoiler:**
Each bingo tile shows:
- **Location name**: Where to find it
- **Sphere**: How deep in progression it is
- **Item**: What item is there (spoiler!)

**Example:**
```json
{
  "location": "Eastern Palace - Compass Chest (Player 1)",
  "sphere": 2
}
```

To complete this tile:
1. Go to Eastern Palace in ALTTP
2. Open the Compass Chest
3. The client will report: "Found Eastern Palace - Compass Chest"
4. Check it off on your bingo tracker

---

## 🎯 Race/Tournament Hosting

### Setup for Competitive Play

#### 1. Generate Identical Seeds
```bash
# All players must use the same seed
python Generate.py --seed 123456789 --spoiler 3 --bingo hard
```

#### 2. Distribute Files
Send each player:
- Their slot data from `AP_123456789.zip`
- The bingo board JSON (same for everyone)
- **NOT the spoiler** (contains solutions)

#### 3. Host Server
```bash
# Host publicly
python MultiServer.py output/AP_123456789.zip --port 38281 --password "race123"
```

#### 4. Race Rules
Define what counts as "bingo completion":
- **Line bingo**: 5 in a row/column/diagonal
- **Blackout**: All 25 tiles
- **Custom**: First to 13 tiles (center + surrounding)

#### 5. Verification
Players must:
- Stream/record gameplay (proof)
- Call out when they complete bingo
- Show final board state

---

## 🛠️ Troubleshooting

### "Where is my bingo file?"
```bash
# Default location
ls -lh output/AP_*_Bingo_*.json

# If you used custom path
ls -lh /your/custom/path/AP_*_Bingo_*.json
```

### "Bingo wasn't generated"
Check that you:
1. Used `--spoiler 3` (or higher) - required for playthrough
2. Used `--bingo <difficulty>` argument
3. Look for errors in console output

### "How do I share the board without spoiling items?"
Option 1: Manually redact items from JSON
```json
{
  "location": "Eastern Palace - Compass Chest",
  "item": "???"  // Hide this
}
```

Option 2: Create a separate "locations-only" export (future enhancement)

### "Can I regenerate just the bingo board?"
No, currently you must regenerate the entire multiworld. The bingo is deterministic, so same seed + difficulty = same board.

---

## 📋 Quick Reference

### Generation Commands
```bash
# Basic generation with bingo
python Generate.py --spoiler 3 --bingo normal

# Custom output path
python Generate.py --spoiler 3 --bingo hard --outputpath ~/my_games

# Specific seed
python Generate.py --seed 123456789 --spoiler 3 --bingo easy
```

### Hosting Commands
```bash
# Host locally
python MultiServer.py output/AP_<seed>.zip

# Host with password
python MultiServer.py output/AP_<seed>.zip --password "secret"

# Host on specific port
python MultiServer.py output/AP_<seed>.zip --port 38281
```

### Finding Files
```bash
# List all output files
ls -lht output/ | head -20

# Find bingo boards
find output/ -name "*_Bingo_*.json"

# View spoiler (careful!)
tail -50 output/AP_*_Spoiler.txt
```

---

## 🚀 Complete Example: Host a Bingo Game

### Full Walkthrough

```bash
# 1. Create player YAML files
cat > player1.yaml << EOF
name: Alice
game: A Link to the Past
A Link to the Past:
  progression_balancing: 50
EOF

cat > player2.yaml << EOF
name: Bob
game: Ocarina of Time
Ocarina of Time:
  logic_rules: glitchless
EOF

# 2. Generate multiworld with bingo
python Generate.py --player_files_path . --spoiler 3 --bingo normal

# 3. Check output
ls -lh output/
# => AP_123456789.zip
# => AP_123456789_Bingo_normal.json
# => AP_123456789_Spoiler.txt

# 4. View bingo board (don't peek at full spoiler!)
tail -30 output/AP_*_Spoiler.txt

# 5. Start server
python MultiServer.py output/AP_*.zip

# 6. Connect clients (in separate terminals)
# Terminal 2: Alice's client
python SNIClient.py  # Then /connect localhost:38281

# Terminal 3: Bob's client
python OoTClient.py  # Then /connect localhost:38281

# 7. Play and track bingo!
# Use printed board or HTML tracker
```

---

## 💡 Tips & Best Practices

### For Players
- **Print the board** before playing (don't rely on memory)
- **Use dual monitors** - game on one, tracker on other
- **Mark sphere numbers** to prioritize early locations
- **Coordinate with team** in multiworld (avoid duplicates)

### For Hosts
- **Test locally first** before hosting for others
- **Use persistent hosting** (screen/tmux) for long games
- **Backup the .zip file** - it contains all game data
- **Share bingo JSON** before game starts (not spoiler!)

### For Racers
- **Agree on rules** before race starts
- **Use same seed + difficulty** for fair competition
- **Record gameplay** for verification
- **Define "completion"** clearly (line? blackout? custom?)

---

## 🔮 Future Enhancements

### Planned Client-Side Features (Not Yet Implemented)
- [ ] Built-in bingo UI in clients
- [ ] Auto-tracking of location completion
- [ ] Visual bingo board overlay
- [ ] Real-time sync across players
- [ ] Audio/visual alerts on bingo completion

These would require changes to the Archipelago client code, which is outside the scope of the current bingo generator module.

---

## 📞 Need Help?

- **Can't find output files?** Check `output/` directory or your custom `--outputpath`
- **Server won't start?** Ensure the .zip file exists and is valid
- **Bingo not generating?** Verify `--spoiler 3` and `--bingo <difficulty>` are used
- **Want to track bingo?** Use Solutions 1-5 above (manual, spoiler text, HTML, OBS, external tools)

---

**Ready to play?** Generate your seed with `--bingo`, start the server, and have fun! 🎮
