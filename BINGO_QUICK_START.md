# Bingo Quick Start

Get a bingo board up and running in 3 steps.

---

## Step 1: Generate a Game with Bingo

```bash
cd /home/curt/Code/Archipelago

# Create a player YAML (if you don't have one)
cat > Players/my_player.yaml << 'EOF'
name: MyPlayer
game: ChecksFinder

ChecksFinder:
  progression_balancing: 0
EOF

# Generate with bingo
python Generate.py --spoiler 3 --bingo normal
```

**Output files** (in `output/` directory):
- `AP_<seed>.zip` - Game data for hosting
- `AP_<seed>_Bingo_normal.json` - Your bingo board
- `AP_<seed>_Spoiler.txt` - Includes bingo at the end

---

## Step 2: View Your Bingo Board

### Option A: Text Format (Simple)
```bash
# View the board in your terminal
tail -40 output/AP_*_Spoiler.txt
```

### Option B: JSON Format (For Tools)
```bash
# Pretty-print the JSON
cat output/AP_*_Bingo_*.json | python -m json.tool
```

---

## Step 3: Track During Play (Optional)

### Simple: Print It Out
```bash
# Save to file and print
tail -40 output/AP_*_Spoiler.txt > my_bingo_board.txt
cat my_bingo_board.txt
```

### Advanced: Use Web Tracker

**If you want real-time tracking:**

1. **Start WebHost:**
   ```bash
   python WebHost.py
   ```

   **Note:** If you get a permission error, create `config.yaml` with:
   ```yaml
   PORT: 5000
   ```

2. **Create a room:**
   - Go to http://localhost:5000/
   - Click "Host a Room" or "Upload Multidata"
   - Upload your `AP_<seed>.zip` file
   - You'll be redirected to the room page

3. **Find your tracker ID:**
   - Look at the URL bar: `http://localhost:5000/room/<room-id>`
   - Or click "Tracker" link - the tracker URL is: `http://localhost:5000/tracker/<tracker-id>`
   - The tracker ID is what you need for bingo

4. **Access bingo tracker:**
   - Go to: `http://localhost:5000/bingo/<tracker-id>`
   - Upload your `_Bingo_normal.json` file
   - The board will auto-update as players check locations!

---

## Different Difficulties

```bash
# Easy - more early-game locations
python Generate.py --spoiler 3 --bingo easy

# Normal - balanced mix
python Generate.py --spoiler 3 --bingo normal

# Hard - more late-game locations
python Generate.py --spoiler 3 --bingo hard
```

---

## That's It!

**Questions?** See `BINGO_USAGE_GUIDE.md` for detailed info on hosting, tracking, and troubleshooting.
