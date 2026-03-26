# Bingo Web Tracker - Installation & Usage Guide

A real-time web-based bingo tracker that integrates with Archipelago's WebHost interface.

---

## 🎯 Features

- ✅ **Real-time tracking** - Auto-updates as players check locations
- ✅ **Visual board** - Beautiful 5×5 grid with completion indicators
- ✅ **Line detection** - Highlights completed rows, columns, diagonals
- ✅ **Multi-player support** - Tracks locations across all players
- ✅ **Easy upload** - Drag-and-drop bingo JSON files
- ✅ **Auto-refresh** - Polls every 5 seconds for updates
- ✅ **Mobile-friendly** - Responsive design works on all devices

---

## 📦 Installation

### Files Created

```
WebHostLib/
├── api/
│   └── bingo.py                        # NEW - API endpoints
├── templates/
│   ├── bingo_tracker.html              # NEW - Main tracker UI
│   └── bingo_upload.html               # NEW - Upload page
└── bingo_tracker.py                    # NEW - Flask routes
```

### Step 1: Verify Files Exist

All three new files should be in your Archipelago directory:
```bash
ls -l WebHostLib/api/bingo.py
ls -l WebHostLib/bingo_tracker.py
ls -l WebHostLib/templates/bingo_tracker.html
ls -l WebHostLib/templates/bingo_upload.html
```

### Step 2: No Additional Setup Needed!

The files are automatically loaded by Archipelago's module discovery system in `WebHostLib/__init__.py`.

---

## 🚀 Usage

### Method 1: Upload Bingo Board to Tracker

#### Step 1: Generate a Game with Bingo
```bash
# Generate multiworld with bingo board
python Generate.py --player_files_path ./yamls --spoiler 3 --bingo normal

# Output:
#   output/AP_123456789_MySeed.zip
#   output/AP_123456789_MySeed_Bingo_normal.json  <-- You need this!
```

#### Step 2: Host the Game
```bash
# Start WebHost
python WebHost.py

# Or start MultiServer and get the tracker link
python MultiServer.py output/AP_123456789_MySeed.zip
```

#### Step 3: Open the Room's Tracker
1. Go to http://localhost (your WebHost instance)
2. Navigate to your room's tracker page
3. The tracker URL will be something like:
   ```
   http://localhost/tracker/<tracker-id>
   ```

#### Step 4: Navigate to Bingo Tracker
Add `/bingo/` to the tracker URL:
```
http://localhost/bingo/<tracker-id>
```

Or manually navigate:
```
http://localhost/bingo/<tracker-id>/upload
```

#### Step 5: Upload Your Bingo Board JSON
1. Click "Upload Bingo Board" or drag-and-drop
2. Select `AP_123456789_MySeed_Bingo_normal.json`
3. Click "Upload"
4. You'll be redirected to the tracker!

---

### Method 2: Auto-Detect Bingo Board (Future Enhancement)

If the bingo board JSON is named correctly and placed in the `output/` directory, the tracker will auto-detect it based on the seed name.

**Expected naming convention:**
```
AP_<seed>_<seed_name>_Bingo_<difficulty>.json
```

---

## 🌐 Accessing the Bingo Tracker

### If Hosting Locally (WebHost.py)

```
http://localhost/bingo/<tracker-id>
```

Or if deployed on a server with a domain:
```
https://your-domain.com/bingo/<tracker-id>
```

### Finding Your Tracker ID

1. Go to your room page
2. Look at the URL:
   ```
   http://localhost/room/<room-id>
   ```
3. Or check the tracker page directly:
   ```
   http://localhost/tracker/<tracker-id>
   ```
4. Use the same `<tracker-id>` for the bingo URL

---

## 🎮 Using the Tracker During Gameplay

### The Interface

**Top Stats:**
- **Tiles Completed**: X/25
- **Progress**: X% complete
- **Difficulty**: Easy/Normal/Hard

**Bingo Board:**
- 5×5 grid of tiles
- ✅ Green tiles = completed
- ⬜ Gray tiles = not completed
- Hover for details (item, sphere)

**Completed Lines:**
- Shows when you complete a row, column, or diagonal
- Displays as badges: "Row 1", "Column 3", "Diagonal \"

### Real-Time Updates

The board auto-refreshes every **5 seconds** by:
1. Polling `/api/bingo/<tracker-id>`
2. Checking which locations have been found
3. Updating tile colors and stats
4. Detecting new completed lines

### What Counts as "Completed"?

A tile is marked complete when:
1. The location on the tile has been checked by any player in the room
2. The server has recorded the check in the multisave

**Example:**
```
Tile: "Eastern Palace - Boss (Player 1)"
→ Player 1 defeats the Eastern Palace boss
→ Client sends location check to server
→ Server updates multisave
→ Bingo tracker polls API (within 5 seconds)
→ Tile turns green ✅
```

---

## 🔌 API Endpoints

### GET `/api/bingo/<tracker-id>`
Returns bingo board with completion status.

**Response:**
```json
{
  "board": [
    [
      {
        "location": "Link's House (Player 1)",
        "player": 1,
        "game": "A Link to the Past",
        "sphere": 1,
        "item": "Lamp",
        "location_id": 123,
        "completed": true
      },
      ...
    ]
  ],
  "status": {
    "total_tiles": 25,
    "completed_tiles": 8,
    "completion_percentage": 32.0,
    "completed_lines": ["row_0", "col_2"]
  },
  "seed": "MySeed123",
  "difficulty": "normal"
}
```

### POST `/api/bingo/<tracker-id>/upload`
Upload a bingo board JSON file.

**Request:**
```
Content-Type: multipart/form-data
Body: bingo_file=<JSON file>
```

**Response:**
```json
{
  "success": true,
  "message": "Bingo board uploaded successfully",
  "seed": 123456789,
  "difficulty": "normal"
}
```

### GET `/api/bingo/<tracker-id>/check`
Check if a bingo board is available.

**Response:**
```json
{
  "available": true,
  "seed": "MySeed123"
}
```

---

## 🛠️ Troubleshooting

### "No Bingo Board Found"

**Cause:** No bingo JSON has been uploaded for this tracker.

**Solution:**
1. Click "Upload Bingo Board"
2. Select your `*_Bingo_*.json` file
3. Upload it

### "Room not found" (404 error)

**Cause:** Invalid tracker ID in the URL.

**Solution:**
1. Verify the tracker ID from the room page
2. Make sure the room is currently hosted
3. Check that the MultiServer is running

### Board Not Updating

**Possible causes:**
- Browser tab is inactive (auto-refresh pauses)
- Server connection lost
- Cache issue

**Solutions:**
- Refresh the page manually (F5)
- Check browser console for errors
- Clear cache (Ctrl+Shift+R)

### Tiles Not Marking as Complete

**Possible causes:**
- Location name doesn't match
- Player number mismatch
- Location ID not resolved

**Debug steps:**
1. Check browser console for errors
2. Verify location names match game's data package
3. Confirm players are connected and sending updates

### Upload Fails with "Invalid bingo board format"

**Cause:** JSON file structure is incorrect.

**Solution:**
- Ensure JSON has a `"board"` field
- Board must be a 5×5 array of arrays
- Each tile must have at least: `location`, `player`, `game`, `sphere`, `item`

---

## 🎨 Customization

### Changing Refresh Interval

Edit `bingo_tracker.html`:
```javascript
const REFRESH_INTERVAL = 5000; // Change to 10000 for 10 seconds
```

### Changing Colors

Edit the `<style>` section in `bingo_tracker.html`:
```css
.bingo-tile.completed {
    background: linear-gradient(135deg, #4ecca3 0%, #2a9d8f 100%);
    /* Change these colors */
}
```

### Adding Sound Effects

Add to `bingo_tracker.html` after line completion detection:
```javascript
if (status.completed_lines.length > previousLineCount) {
    const audio = new Audio('/static/assets/bingo_sound.mp3');
    audio.play();
}
```

---

## 🔮 Future Enhancements

### Planned Features
- [ ] **WebSocket support** - Real-time updates without polling
- [ ] **Multiple board support** - Switch between different difficulties
- [ ] **Statistics** - Track completion times, fastest tiles
- [ ] **Filters** - Show only specific players or games
- [ ] **Export** - Download completion history as CSV
- [ ] **Achievements** - Badges for special completions

### Possible Integrations
- [ ] **OBS overlay** - Stream-friendly bingo display
- [ ] **Discord bot** - Announce completions
- [ ] **Leaderboards** - Compare with other players
- [ ] **Replay mode** - Watch how the board was completed

---

## 📁 File Storage

### Where Uploaded Boards Are Saved

```
output/
└── bingo_boards/
    └── <tracker-id>.json    # Uploaded boards
```

### Auto-Detection Path

The API tries to find bingo boards in this order:
1. `output/bingo_boards/<tracker-id>.json` (uploaded)
2. `output/AP_*<seed_name>*_Bingo_*.json` (generated)

---

## 🧪 Testing

### Test with Example Data

```bash
# 1. Create a test bingo board
cat > test_bingo.json << 'EOF'
{
  "version": "1.0",
  "seed": 123456,
  "difficulty": "test",
  "board": [
    [
      {"location": "Link's House", "player": 1, "game": "A Link to the Past", "sphere": 1, "item": "Lamp"},
      {"location": "Sanctuary", "player": 1, "game": "A Link to the Past", "sphere": 1, "item": "Key"},
      ...
    ],
    ...
  ]
}
EOF

# 2. Start WebHost
python WebHost.py

# 3. Create a room and get tracker ID

# 4. Upload test_bingo.json via the upload page

# 5. Watch tiles update as you check locations!
```

---

## 📊 Performance Notes

- **Polling Overhead**: ~5 seconds between updates is a good balance
- **Cache Duration**: API responses cached for 10 seconds
- **Concurrent Users**: Scales well with Flask's threading
- **Database Load**: Minimal (only reads from existing tracker data)

---

## 🤝 Contributing

Want to improve the bingo tracker? Here's how:

### Adding New Features

1. **Backend (Python)**: Edit `WebHostLib/api/bingo.py`
2. **Frontend (HTML/JS)**: Edit `WebHostLib/templates/bingo_tracker.html`
3. **Routes**: Edit `WebHostLib/bingo_tracker.py`

### Testing Changes

```bash
# Restart WebHost to reload changes
pkill -f WebHost.py
python WebHost.py
```

---

## 📞 Support

### Common Questions

**Q: Can I use this without WebHost?**
A: No, it requires the WebHost infrastructure (Flask app, Room database).

**Q: Can I deploy this on a public server?**
A: Yes! If you deploy WebHost to a server, the bingo module will work the same way.

**Q: Can multiple people view the same bingo board?**
A: Yes! Share the tracker URL and everyone sees the same real-time updates.

**Q: Does this affect game performance?**
A: No. It only reads existing tracker data; doesn't interfere with gameplay.

---

## 🎓 Summary

The Bingo Web Tracker provides a polished, real-time interface for tracking bingo boards during Archipelago gameplay. It integrates seamlessly with the existing WebHost infrastructure and requires minimal setup.

**Key Points:**
- ✅ Drop-in module (no core changes needed)
- ✅ Real-time updates via API polling
- ✅ Beautiful, responsive UI
- ✅ Multi-player support
- ✅ Easy to use (just upload JSON and play!)

**Next Steps:**
1. Generate a seed with `--bingo`
2. Host the game
3. Upload bingo JSON to tracker
4. Watch tiles complete in real-time!

Enjoy your bingo runs! 🎯
