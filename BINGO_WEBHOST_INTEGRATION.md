# Bingo WebHost Integration

Integration of Bingo Tracker into Archipelago WebHost interface.

---

## What Was Added

### 1. **Room Page Link** (`hostRoom.html`)

When hosting an Archipelago game, the room page now includes a link to the Bingo Tracker alongside the existing tracker links.

**Before:**
```
This room has a Multiworld Tracker and a Sphere Tracker enabled.
```

**After:**
```
This room has a Multiworld Tracker, a Sphere Tracker, and a Bingo Tracker enabled.
```

**Location:** `/room/<room_id>`

---

### 2. **Multiworld Tracker Navigation** (`multitracker.html`)

The multiworld item tracker now includes a prominent Bingo Tracker link at the top of the page.

**Features:**
- 🎯 Large, visible link to bingo tracker
- ✓ Real-time status indicator (checks if board is available)
- ⚠ Shows warning if no board uploaded yet

**What you see:**
```
┌─────────────────────────────────────────────┐
│  🎯 View Bingo Tracker  ✓ Board Available  │
└─────────────────────────────────────────────┘
```

Or if no board exists:
```
┌───────────────────────────────────────────────────────┐
│  🎯 View Bingo Tracker  ⚠ No board yet - Upload one! │
└───────────────────────────────────────────────────────┘
```

**Location:** `/tracker/<tracker_id>`

---

### 3. **Bingo Tracker Navigation** (`bingo_tracker.html`)

The bingo tracker page now includes links back to the other trackers for easy navigation.

**What you see:**
```
┌─────────────────────────────────────────┐
│  📊 Multiworld Tracker | 🔮 Sphere Tracker  │
└─────────────────────────────────────────┘

        🎯 Archipelago Bingo Tracker
```

**Location:** `/bingo/<tracker_id>`

---

## User Flow

### Scenario 1: Hosting a Game with Bingo

1. **Generate multiworld with bingo:**
   ```bash
   python Generate.py --spoiler 3 --bingo coop:normal
   ```

2. **Upload to WebHost:**
   - Upload the `.zip` file
   - Upload the `*_Bingo_coop_normal.json` file (optional, can upload later)

3. **Start hosting:**
   - Room page shows: "This room has a Bingo Tracker enabled"
   - Click the Bingo Tracker link

4. **View bingo tracker:**
   - If board uploaded: See the 5x5 bingo board with real-time completion
   - If not uploaded: See upload page with instructions

5. **During gameplay:**
   - Navigate between trackers easily:
     - Multiworld Tracker (item checks)
     - Sphere Tracker (progression depth)
     - Bingo Tracker (bingo board progress)

---

### Scenario 2: Accessing Different Trackers

**From Room Page:**
```
Room Page
  ├─→ Click "Multiworld Tracker" → Item check tracker
  ├─→ Click "Sphere Tracker" → Sphere progression tracker
  └─→ Click "Bingo Tracker" → Bingo board tracker
```

**From Multiworld Tracker:**
```
Multiworld Tracker (item checks)
  └─→ Click "🎯 View Bingo Tracker" at top → Bingo tracker
```

**From Bingo Tracker:**
```
Bingo Tracker
  ├─→ Click "📊 Multiworld Tracker" → Back to item tracker
  └─→ Click "🔮 Sphere Tracker" → Sphere tracker
```

---

## Visual Design

### Room Page Link
- **Style:** Inline text link
- **Color:** Default link color
- **Location:** Info section at top of room page

### Multiworld Tracker Navigation
- **Style:** Prominent banner at top
- **Background:** Dark blue (#16213e)
- **Link color:** Teal (#4ecca3)
- **Font size:** 1.1em (larger than normal text)
- **Status indicator:** Real-time check via AJAX

### Bingo Tracker Navigation
- **Style:** Clean banner at top
- **Background:** Dark blue (#16213e)
- **Link color:** Teal (#4ecca3)
- **Layout:** Two links side-by-side with emojis

---

## Technical Implementation

### Files Modified

#### 1. `WebHostLib/templates/hostRoom.html`
**Change:** Added bingo tracker link to room info section

**Before:**
```html
This room has a <a href="...">Multiworld Tracker</a>
and a <a href="...">Sphere Tracker</a> enabled.
```

**After:**
```html
This room has a <a href="...">Multiworld Tracker</a>,
a <a href="...">Sphere Tracker</a>,
and a <a href="...">Bingo Tracker</a> enabled.
```

#### 2. `WebHostLib/templates/multitracker.html`
**Change:** Added bingo tracker navigation banner with real-time status check

**Added:**
- Navigation banner with link to bingo tracker
- JavaScript AJAX call to `/api/bingo/<tracker>/check`
- Status indicator (available, not available, loading)
- CSS animation for loading spinner

#### 3. `WebHostLib/templates/bingo_tracker.html`
**Change:** Added navigation links back to other trackers

**Added:**
- Navigation banner with links to:
  - Multiworld Tracker (📊)
  - Sphere Tracker (🔮)

---

## API Endpoints Used

### Check Bingo Availability
```
GET /api/bingo/<tracker_id>/check
```

**Response:**
```json
{
  "available": true,
  "seed": "MySeedName"
}
```

**Used by:** Multiworld tracker page to show status indicator

---

## Testing

### Manual Testing Steps

1. **Test Room Page Link:**
   ```
   ✓ Generate seed with bingo
   ✓ Upload to webhost
   ✓ Check room page shows bingo tracker link
   ✓ Click link → navigates to bingo tracker
   ```

2. **Test Multiworld Tracker Navigation:**
   ```
   ✓ Go to multiworld tracker
   ✓ See bingo tracker banner at top
   ✓ Status indicator shows:
      - "Checking..." (loading)
      - "✓ Board Available" (if uploaded)
      - "⚠ No board yet" (if not uploaded)
   ✓ Click link → navigates to bingo tracker
   ```

3. **Test Bingo Tracker Navigation:**
   ```
   ✓ Go to bingo tracker
   ✓ See navigation links at top
   ✓ Click "Multiworld Tracker" → back to item tracker
   ✓ Click "Sphere Tracker" → sphere tracker
   ```

4. **Test Navigation Flow:**
   ```
   Room Page → Multiworld Tracker → Bingo Tracker → Back to Multiworld
   Room Page → Bingo Tracker → Multiworld Tracker
   Room Page → Sphere Tracker → [no bingo link here, go back to multiworld]
   ```

---

## Browser Compatibility

### JavaScript Features Used
- `async/await` (ES2017)
- `fetch()` API
- CSS animations

**Supported Browsers:**
- ✅ Chrome 55+
- ✅ Firefox 52+
- ✅ Safari 11+
- ✅ Edge 79+

**Fallback:**
- If JavaScript fails, status indicator shows default text
- Link still works without JavaScript
- Graceful degradation for older browsers

---

## User Experience Improvements

### Before This Change
- Users had no way to access bingo tracker from tracker pages
- Had to manually type URL or use back button to find room page
- No indication if bingo board was uploaded
- Difficult to switch between different tracker views

### After This Change
- ✅ One-click access to bingo tracker from any tracker page
- ✅ Clear indication of board availability
- ✅ Easy navigation between all three tracker types
- ✅ Seamless workflow during gameplay
- ✅ All trackers interconnected

---

## Future Enhancements

### Potential Improvements

1. **Unified Tracker Navigation Bar**
   - Create a consistent navigation component across all tracker pages
   - Always show: Multiworld | Sphere | Bingo tabs

2. **Bingo Preview on Multiworld Tracker**
   - Show mini bingo board (2x2 or 3x3) in sidebar
   - Click to expand to full tracker

3. **Completion Notifications**
   - Show toast notification on multiworld tracker when bingo line completed
   - Badge indicator on bingo link showing number of completed lines

4. **Tracker Integration**
   - Show bingo status in player rows on multiworld tracker
   - Column: "Bingo Progress: 8/25 (32%)"

5. **Auto-Navigation**
   - When bingo line completed, option to auto-navigate to bingo tracker
   - Celebration animation

---

## Configuration

No configuration needed! The links appear automatically when:
- Room has a tracker enabled
- Bingo tracker page exists

**Note:** The bingo board must be uploaded separately. If not uploaded:
- Links still appear (not hidden)
- Bingo tracker page shows upload option
- Status indicator shows "No board yet"

---

## Accessibility

### Features
- ✅ Semantic HTML links
- ✅ Emoji indicators for visual users
- ✅ Text descriptions for screen readers
- ✅ Keyboard navigation (tab through links)
- ✅ Clear focus indicators

### ARIA Attributes (Future)
Could add:
```html
<nav aria-label="Tracker Navigation">
  <a href="..." aria-label="View Bingo Tracker">...</a>
</nav>
```

---

## Known Limitations

1. **Status Check Delay**
   - AJAX call takes ~100-300ms
   - Shows "Checking..." spinner during load
   - Cached on client side (no refresh on navigation)

2. **No Sphere Tracker → Bingo Link**
   - Sphere tracker doesn't have bingo link (yet)
   - Users must go: Sphere → Multiworld → Bingo
   - Could be added in future

3. **Upload Workflow**
   - Bingo board must be uploaded separately
   - Not integrated with seed upload
   - Manual process for now

---

## Summary

### What Users See

1. **Room Page:**
   - "... and a Bingo Tracker enabled."

2. **Multiworld Tracker:**
   - Big button: "🎯 View Bingo Tracker ✓ Board Available"

3. **Bingo Tracker:**
   - Nav links: "📊 Multiworld Tracker | 🔮 Sphere Tracker"

### Navigation Paths

```
        ┌─────────────┐
        │  Room Page  │
        └──────┬──────┘
               │
       ┌───────┼───────┐
       │       │       │
       ▼       ▼       ▼
  ┌────────┐ ┌────────┐ ┌────────┐
  │Multiw. │ │Sphere  │ │ Bingo  │
  │Tracker │ │Tracker │ │Tracker │
  └────────┘ └────────┘ └────────┘
       │                     │
       │◄────────────────────┘
       └─────────────────────►
```

**Result:** Seamless navigation between all tracker types! 🎉

---

**Last Updated:** 2026-02-08
**Files Modified:** 3 templates
**New API Calls:** 1 (availability check)
