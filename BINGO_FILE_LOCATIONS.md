# Bingo File Locations - Visual Guide

## 📂 Where Everything Is Saved

### Directory Structure After Generation

```
/home/curt/Code/Archipelago/
│
├── Generate.py              # Run this to generate games
├── MultiServer.py           # Run this to host games
├── bingo.py                 # The bingo module (already here!)
│
└── output/                  # ⭐ ALL GENERATED FILES GO HERE
    │
    ├── AP_123456789_MySeed.zip                # Main multiworld data
    │   └── (Contains all player slot data)    # Give this to MultiServer.py
    │
    ├── AP_123456789_MySeed_Bingo_normal.json  # ⭐ BINGO BOARD (JSON)
    │   └── {                                   # This is what you want!
    │       "board": [[...tiles...]],           # Open this to see bingo
    │       "difficulty": "normal",
    │       ...
    │     }
    │
    └── AP_123456789_MySeed_Spoiler.txt        # Spoiler log
        └── (Last 30 lines contain bingo)      # Also has bingo at end
```

---

## 🎯 The Files You Care About

### 1. **Bingo Board JSON** (For Tracking)
```
output/AP_123456789_MySeed_Bingo_normal.json
```

**What it contains:**
- 5×5 grid of locations
- Player assignments
- Sphere depths (difficulty info)
- Items at each location (spoiler!)

**Use it for:**
- Manual tracking during gameplay
- Creating HTML tracker
- Sharing with other players (hide items!)
- OBS overlay

### 2. **Multiworld ZIP** (For Hosting)
```
output/AP_123456789_MySeed.zip
```

**What it contains:**
- All player slot data
- Item/location mappings
- Server configuration

**Use it for:**
- Hosting: `python MultiServer.py output/AP_*.zip`
- Distribution to players
- Uploading to a self-hosted web interface (if available)

### 3. **Spoiler Text** (For Peeking)
```
output/AP_123456789_MySeed_Spoiler.txt
```

**What it contains:**
- Full playthrough solution
- All item locations
- **Bingo board at the end** (formatted text)

**Use it for:**
- Viewing bingo board without JSON parser
- Checking what items are where (spoiler!)
- Debugging generation issues

---

## 🚀 Quick Start Commands

### Generate with Bingo
```bash
cd /home/curt/Code/Archipelago

# Create a test YAML
cat > test_player.yaml << 'EOF'
name: TestPlayer
game: A Link to the Past

A Link to the Past:
  progression_balancing: 50
EOF

# Generate
python Generate.py --player_files_path . --spoiler 3 --bingo normal

# Check output
ls -lh output/
```

**Expected output:**
```
total 128K
-rw-r--r-- 1 curt curt  85K Feb  7 15:00 AP_123456789_TestPlayer.zip
-rw-r--r-- 1 curt curt   5K Feb  7 15:00 AP_123456789_TestPlayer_Bingo_normal.json
-rw-r--r-- 1 curt curt  25K Feb  7 15:00 AP_123456789_TestPlayer_Spoiler.txt
```

---

## 📊 View Your Bingo Board

### Option 1: View JSON (Machine-Readable)
```bash
# Pretty-print the JSON
cat output/AP_*_Bingo_*.json | python -m json.tool | less
```

### Option 2: View Spoiler Text (Human-Readable)
```bash
# Show last 40 lines (includes bingo board)
tail -40 output/AP_*_Spoiler.txt
```

**Example output:**
```
================================================================================
BINGO BOARD - Difficulty: NORMAL
================================================================================

Link's House [S1]              | Eastern Palace - Boss [S2]    | Desert Palace - Big Key [S3]
Hyrule Castle - Zelda's Cell   | Tower of Hera - Big Chest     | Swamp Palace - Entrance [S5]
...

================================================================================
Legend: [SN] = Sphere N (progression depth)
================================================================================
```

### Option 3: View Raw JSON Data
```bash
# Use jq for pretty colors (if installed)
cat output/AP_*_Bingo_*.json | jq .

# Or just cat
cat output/AP_*_Bingo_*.json
```

---

## 🌐 Host Your Game

### Method 1: Host Locally (Same Computer)
```bash
# Start server
python MultiServer.py output/AP_*.zip

# Server starts on port 38281
# Players connect to: localhost:38281
```

### Method 2: Host on LAN (Local Network)
```bash
# Find your local IP
ip addr show | grep "inet " | grep -v 127.0.0.1

# Example output: 192.168.1.100

# Start server
python MultiServer.py output/AP_*.zip --port 38281

# Players connect to: 192.168.1.100:38281
```

### Method 3: Host on Internet (Remote Players)
```bash
# On your server (with public IP)
python MultiServer.py output/AP_*.zip --port 38281

# Forward port 38281 in your router
# Players connect to: your.public.ip:38281
```

---

## 📱 Connect Clients

### Once Server is Running...

**Each player needs to:**
1. Launch their game-specific client
2. Connect to the server

**Example (A Link to the Past):**
```bash
# Player launches SNIClient
python SNIClient.py

# In the client interface
/connect localhost:38281

# Or for remote server
/connect 192.168.1.100:38281
```

**Other game clients:**
- **Ocarina of Time**: `python OoTClient.py`
- **Factorio**: Launch game, use built-in mod
- **Dark Souls 3**: `python DS3Client.py`
- **etc.**: Check `worlds/<game>/docs/setup_en.md`

---

## 🎮 Track Your Bingo During Play

### The Reality: No Built-In Tracking

**Important:** The bingo board is generated, but **Archipelago doesn't track it automatically**. You need to track it yourself.

### Recommended: Print the Board
```bash
# Generate a printable version
tail -40 output/AP_*_Spoiler.txt > my_bingo_board.txt

# Print this file or view on second monitor
cat my_bingo_board.txt
```

### Alternative: Use HTML Tracker

Create `bingo_tracker.html`:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Bingo Tracker</title>
    <style>
        table { border-collapse: collapse; margin: 20px; }
        td {
            border: 2px solid #000;
            width: 150px;
            height: 100px;
            text-align: center;
            cursor: pointer;
            padding: 5px;
        }
        td.checked {
            background-color: #90EE90;
            text-decoration: line-through;
        }
    </style>
</head>
<body>
    <h1>Archipelago Bingo</h1>
    <table id="board"></table>
    <script>
        // Paste your bingo JSON here
        fetch('AP_123456789_Bingo_normal.json')
            .then(r => r.json())
            .then(data => {
                const board = document.getElementById('board');
                data.board.forEach(row => {
                    const tr = document.createElement('tr');
                    row.forEach(tile => {
                        const td = document.createElement('td');
                        td.textContent = tile.location + ' [S' + tile.sphere + ']';
                        td.onclick = () => td.classList.toggle('checked');
                        tr.appendChild(td);
                    });
                    board.appendChild(tr);
                });
            });
    </script>
</body>
</html>
```

Open in browser, click tiles to check them off!

---

## 🔍 Finding Specific Files

### List All Generated Files
```bash
ls -lht output/ | head -20
```

### Find Bingo Boards Only
```bash
find output/ -name "*_Bingo_*.json"
```

### Find Latest Generation
```bash
ls -t output/*.zip | head -1
```

### Find Specific Seed
```bash
ls output/AP_123456789*
```

---

## 🎯 Race/Competition Setup

### For Tournament Organizers

**Generate the seed:**
```bash
python Generate.py --seed 123456789 --spoiler 3 --bingo hard
```

**Distribute to players:**
1. **Share:** `output/AP_123456789.zip` (multiworld data)
2. **Share:** `output/AP_123456789_Bingo_hard.json` (bingo board)
3. **HIDE:** `output/AP_123456789_Spoiler.txt` (contains solutions!)

**Host the server:**
```bash
python MultiServer.py output/AP_123456789.zip --password "race_password"
```

**Rules:**
- First to complete a line = winner
- Or first to blackout (all 25) = winner
- Must show proof (stream/recording)

---

## 🛠️ Troubleshooting

### "I can't find my bingo file!"
```bash
# Check default location
ls output/

# Check if generation succeeded
python Generate.py --spoiler 3 --bingo normal | grep -i bingo

# Check for errors
python Generate.py --spoiler 3 --bingo normal 2>&1 | grep -i error
```

### "The output directory is empty!"
```bash
# Make sure you're in the Archipelago directory
pwd
# Should be: /home/curt/Code/Archipelago

# Try generating again
python Generate.py --player_files_path . --spoiler 3 --bingo normal
```

### "Server won't start!"
```bash
# Check if .zip exists
ls -lh output/*.zip

# Check if port is in use
lsof -i :38281

# Try different port
python MultiServer.py output/AP_*.zip --port 38282
```

---

## 📋 Complete File Manifest

After successful generation, you should see:

```
output/
├── AP_<seed>_<name>.zip                 # Required for hosting
├── AP_<seed>_<name>_Bingo_<diff>.json  # Bingo board (if --bingo used)
└── AP_<seed>_<name>_Spoiler.txt        # Spoiler (if --spoiler used)
```

**File sizes:**
- `.zip`: 50-500 KB (depends on number of players/items)
- `_Bingo_*.json`: 4-6 KB (always ~5KB)
- `_Spoiler.txt`: 10-100 KB (depends on playthrough length)

---

## 🎓 Summary

### Key Points
1. **Files go to** `output/` by default
2. **Bingo JSON** is `AP_*_Bingo_*.json`
3. **Host with** `python MultiServer.py output/AP_*.zip`
4. **Track manually** (no auto-tracking yet)
5. **View in spoiler** (last 40 lines) for human-readable version

### Next Steps
1. Generate a test seed (see Quick Start above)
2. Check that files appear in `output/`
3. View the bingo board (JSON or spoiler text)
4. Host the server
5. Connect and play!

---

**Questions?** See `BINGO_USAGE_GUIDE.md` for detailed hosting and tracking info!
