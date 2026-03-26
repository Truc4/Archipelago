# Bingo Web Tracker - 5-Minute Quick Start

Get the web-based bingo tracker running in 5 minutes!

---

## ✅ Files Created

All files are already in place:

```
✓ WebHostLib/api/bingo.py
✓ WebHostLib/bingo_tracker.py
✓ WebHostLib/templates/bingo_tracker.html
✓ WebHostLib/templates/bingo_upload.html
```

**No installation needed!** Flask auto-loads these modules.

---

## 🚀 Quick Start (5 Steps)

### Step 1: Generate a Seed with Bingo (1 min)

```bash
cd /home/curt/Code/Archipelago

# Create a test player file
cat > test_player.yaml << 'EOF'
name: TestPlayer
game: A Link to the Past

A Link to the Past:
  progression_balancing: 50
EOF

# Generate with bingo
python Generate.py --player_files_path . --spoiler 3 --bingo normal
```

**Output:**
- `output/AP_<seed>_TestPlayer.zip`
- `output/AP_<seed>_TestPlayer_Bingo_normal.json` ⬅️ You need this!

---

### Step 2: Start WebHost (30 seconds)

```bash
python WebHost.py
```

**Output:**
```
Serving on http://0.0.0.0:80
```

Open http://localhost/ in your browser.

---

### Step 3: Create a Room (1 min)

1. Click "Host Game"
2. Upload `output/AP_<seed>_TestPlayer.zip`
3. Click "Create New Room"
4. **Copy the Tracker ID** from the URL:
   ```
   http://localhost/tracker/AbC123DeF456...
                            ^^^^^^^^^^^^^^^^ This is your tracker ID
   ```

---

### Step 4: Open Bingo Tracker (30 seconds)

Navigate to:
```
http://localhost/bingo/AbC123DeF456...
                       ^^^^^^^^^^^^^^^^ Use your tracker ID
```

You'll see: **"No Bingo Board Found"**

Click: **"Upload Bingo Board"**

---

### Step 5: Upload Bingo JSON (30 seconds)

1. Drag and drop: `output/AP_<seed>_TestPlayer_Bingo_normal.json`
2. Click "Upload Bingo Board"
3. **Done!** You'll see your 5×5 bingo board

---

## 🎮 Test It Out

### Connect a Client

```bash
# Terminal 2
python SNIClient.py

# In the client
/connect localhost:38281
```

### Play the Game

As you check locations in the game, watch the bingo board:
- Tiles turn **green** when completed ✅
- Stats update in real-time
- Lines are detected automatically

---

## 📊 What You'll See

### The Bingo Board

```
╔═══════════════════════════════════════╗
║   Bingo Tracker - TestPlayer          ║
║   Completed: 3/25  |  Progress: 12%   ║
╚═══════════════════════════════════════╝

┌────────────┬────────────┬────────────┬────────────┬────────────┐
│  ✓ Link's  │    Sanct-  │   Eastern  │  ✓ Desert  │   Hyrule   │
│    House   │    uary    │   Palace   │   Palace   │   Castle   │
│    [S1]    │    [S1]    │    [S2]    │    [S3]    │    [S2]    │
├────────────┼────────────┼────────────┼────────────┼────────────┤
│   Tower    │  ✓ Swamp   │   Thieves  │   Ice      │   Skull    │
│  of Hera   │   Palace   │   Town     │  Palace    │   Woods    │
│    [S4]    │    [S5]    │    [S7]    │    [S6]    │    [S6]    │
└────────────┴────────────┴────────────┴────────────┴────────────┘
...
```

- **Green tiles** = Completed ✅
- **Gray tiles** = Not completed yet
- **[SN]** = Sphere number (difficulty indicator)

### Auto-Refresh

The board updates **every 5 seconds** automatically. No need to refresh!

---

## 🔗 URLs Reference

| Page | URL |
|------|-----|
| WebHost Home | `http://localhost/` |
| Room Page | `http://localhost/room/<room-id>` |
| Tracker Page | `http://localhost/tracker/<tracker-id>` |
| **Bingo Tracker** | `http://localhost/bingo/<tracker-id>` ⭐ |
| Bingo Upload | `http://localhost/bingo/<tracker-id>/upload` |
| API Endpoint | `http://localhost/api/bingo/<tracker-id>` |

---

## 🛠️ Troubleshooting

### "No Bingo Board Found"

➡️ **Solution:** Upload the JSON file via the upload page

### "Room not found" (404)

➡️ **Solution:** Check that:
- WebHost is running
- You're using the correct tracker ID
- The room is created

### Board Not Updating

➡️ **Solution:**
- Refresh the page (F5)
- Check browser console for errors
- Verify server is still running

### Can't Upload File

➡️ **Solution:**
- Ensure file is `.json`
- Check file is valid JSON
- Try smaller file size

---

## 📱 Mobile Access

Works great on phones/tablets!

1. Find your computer's local IP:
   ```bash
   ip addr show | grep "inet "
   ```
2. On phone, go to: `http://192.168.x.x/bingo/<tracker-id>`
3. Bookmark it for easy access during play!

---

## 🎯 Advanced: Auto-Host Workflow

```bash
# 1. Generate multiple seeds
for i in {1..5}; do
    python Generate.py --seed $i --spoiler 3 --bingo hard
done

# 2. Start WebHost
python WebHost.py &

# 3. Auto-open bingo tracker
# (After creating room and getting tracker ID)
xdg-open "http://localhost/bingo/<tracker-id>"

# 4. Play and track!
```

---

## 📖 Full Documentation

- **Usage Guide:** `BINGO_WEB_TRACKER.md` (detailed usage, API docs)
- **Architecture:** `BINGO_WEB_SUMMARY.md` (technical details)
- **This File:** Quick start only

---

## ✨ Tips

### For Streamers

- Open bingo tracker in OBS browser source
- Set width: 1000px, height: 800px
- Position in corner of stream

### For Racers

- Share tracker URL with competitors
- Everyone sees the same real-time board
- First to complete a line wins!

### For Casual Play

- Use on second monitor
- Check off mentally as you play
- Celebrate when lines complete!

---

## 🎉 That's It!

You now have a fully functional web-based bingo tracker!

**Recap:**
1. ✅ Generate seed with `--bingo`
2. ✅ Start `python WebHost.py`
3. ✅ Create room
4. ✅ Go to `/bingo/<tracker-id>`
5. ✅ Upload JSON
6. ✅ Play and watch tiles complete!

**Need more help?** See `BINGO_WEB_TRACKER.md` for detailed guide.

---

**Happy Bingo! 🎯**
