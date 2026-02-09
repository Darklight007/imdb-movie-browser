# Changelog

## [Unreleased]

### Added - Genre Include/Exclude Feature (2026-02-08)

**Feature:** Genre buttons now support 3 states like the desktop GUI:
- **Normal** (gray) - Genre is ignored
- **Include** (green with +) - Must have this genre
- **Exclude** (red with -) - Must NOT have this genre

**How to use:**
- Click genre button once → + (include, green)
- Click again → - (exclude, red)
- Click again → back to normal (gray)

**Files Modified:**

1. **templates/index.html**
   - Updated genre button click handler to cycle through 3 states
   - Added `genreStates` Map to track each genre's state
   - Updated form submission to send both `genres_include` and `genres_exclude` arrays
   - Updated `resetForm()` to clear genre states properly

2. **static/css/style.css**
   - Added `.genre-btn.genre-include` class (light green #c8e6c9, dark green text #2e7d32)
   - Added `.genre-btn.genre-exclude` class (light red #ffcdd2, dark red text #c62828)
   - Color scheme matches desktop GUI

3. **app.py**
   - Added `genres_exclude` parameter handling in `build_query()` function
   - Exclude genres use `NOT LIKE` SQL condition
   - Multiple exclude genres combined with AND logic

**Backend Logic:**
```python
# Include genres (OR/AND based on mode)
if genres_include:
    # ... include logic

# Exclude genres (always AND)
if genres_exclude:
    for g in genres_exclude:
        query += " AND genres NOT LIKE ?"
        params.append(f"%{g}%")
```

**Frontend Logic:**
```javascript
const GENRE_NORMAL = 0;
const GENRE_INCLUDE = 1;
const GENRE_EXCLUDE = 2;

// Cycle: normal → include → exclude → normal
```

**Example Use Cases:**

1. **Find Action movies without Horror:**
   - Click "Action" once (green +)
   - Click "Horror" twice (red -)

2. **Find Drama or Romance, but not Comedy:**
   - Click "Drama" once (green +)
   - Click "Romance" once (green +)
   - Select "Match ANY" radio button
   - Click "Comedy" twice (red -)

3. **Find Sci-Fi AND Thriller, excluding Action:**
   - Click "Sci-Fi" once (green +)
   - Click "Thriller" once (green +)
   - Select "Match ALL" radio button
   - Click "Action" twice (red -)

**Testing:**

To test locally:
```bash
./run_local.sh
# Visit http://localhost:5000
# Try clicking genre buttons to see + and - states
```

## Version History

### v1.1 (2026-02-08)
- Added genre include/exclude functionality

### v1.0 (2026-02-08)
- Initial Flask web app conversion from desktop GUI
- All desktop features ported
- Responsive design
- Production-ready deployment
