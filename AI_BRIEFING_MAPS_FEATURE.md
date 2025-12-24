# AI Briefing - Naver Maps Fallback Feature

## Problem

Some restaurants do not have AI briefing available on **Naver Place**, but do have it when searched on **Naver Maps**. The original script only checked Naver Place, missing AI briefings that were only available on Maps.

## Solution

Added a fallback mechanism that checks **both** sources:
1. **First**: Check Naver Place (primary source)
2. **If not found**: Check Naver Maps (fallback)
3. Use whichever source has the AI briefing available

## Implementation

### New Function: `get_ai_briefing_from_naver_maps()`

```python
def get_ai_briefing_from_naver_maps(driver, place_id, debug=True):
    """
    Try to extract AI briefing from Naver Maps (as opposed to Naver Place).
    Some restaurants have AI briefing only on Maps, not on Place.
    """
```

This function tries **two different Naver Maps URL structures**:

1. **Mobile Maps URL**:
   ```
   https://m.map.naver.com/search2/site.naver?query=&type=SITE_1&id={place_id}
   ```

2. **Desktop Maps URL**:
   ```
   https://map.naver.com/p/search/{place_id}
   ```

Both URLs are tried to maximize the chance of finding the AI briefing.

### Updated Main Function Logic

```python
# --- AI Briefing ---
results['ai_briefing'] = ""
ai_source = ""

# First, try Naver Place (current page)
if 'AI 브리핑' in body_text:
    results['ai_briefing'] = clean_ai_briefing(raw_ai)
    ai_source = "Naver Place"

# If not found on Place, try Naver Maps
if not results['ai_briefing']:
    maps_briefing = get_ai_briefing_from_naver_maps(driver, place_id)
    if maps_briefing:
        results['ai_briefing'] = maps_briefing
        ai_source = "Naver Maps"
```

### Source Tracking

The script now tracks **where** the AI briefing was found and includes this information in the output:

```python
results['ai_source'] = ai_source if ai_source else None
```

## Output Format

When AI briefing is found, the output now shows the source:

```
🤖 AI Briefing:
──────────────────────────────────────── (Source: Naver Maps)
[AI briefing content here]
────────────────────────────────────────
```

If no AI briefing is found on either source:
```
🤖 AI Briefing:
   (Not available on either Naver Place or Naver Maps)
```

## Debug Output

When `debug=True`, the script shows the search process:

```
[DEBUG] Found AI briefing on Naver Place
✓ AI briefing found on Naver Place
```

Or if it needs to check Maps:

```
[DEBUG] AI briefing not found on Place, checking Maps...
[DEBUG] Checking Naver Maps for AI briefing...
[DEBUG] Found AI briefing on Naver Maps!
✓ AI briefing found on Naver Maps
```

Or if not found anywhere:

```
[DEBUG] AI briefing not found on Place, checking Maps...
[DEBUG] Checking Naver Maps for AI briefing...
⚠ No AI briefing found on either Place or Maps
```

## Benefits

✅ **Comprehensive Coverage**: Checks both major Naver platforms
✅ **Automatic Fallback**: Seamlessly tries Maps if Place doesn't have it
✅ **Source Transparency**: Shows which platform provided the AI briefing
✅ **No Breaking Changes**: Works with existing code, just provides more data
✅ **Debug Visibility**: Clear logging of the search process

## Technical Details

### URL Structures Used

| Platform | URL Pattern | Purpose |
|----------|-------------|---------|
| Naver Place | `https://m.place.naver.com/restaurant/{place_id}/home` | Primary source |
| Naver Maps Mobile | `https://m.map.naver.com/search2/site.naver?query=&type=SITE_1&id={place_id}` | Fallback option 1 |
| Naver Maps Desktop | `https://map.naver.com/p/search/{place_id}` | Fallback option 2 |

### Processing Steps

1. Load Naver Place home page
2. Check for "AI 브리핑" or "AI브리핑" in page text
3. If found, extract and clean the briefing
4. If NOT found:
   - Navigate to Naver Maps mobile URL
   - Scroll and wait for content to load
   - Check for AI briefing
   - If still not found, try desktop Maps URL
   - Extract and clean if found

### Wait Times

- **3 seconds**: After loading each Maps page
- **1 second**: After scrolling to load dynamic content

These wait times ensure JavaScript-rendered content is fully loaded.

## Example Usage

```python
from naver_place_scraper import get_full_restaurant_data

data = get_full_restaurant_data("옥수동화덕피자", debug=True)

if data['ai_briefing']:
    print(f"AI Briefing from {data['ai_source']}:")
    print(data['ai_briefing'])
else:
    print("No AI briefing available")
```

## Testing

To test this feature with restaurants that might have AI briefing only on Maps:

1. Run the script with debug mode enabled
2. Watch the console output to see which source is checked
3. Verify the AI briefing content and source attribution

```bash
python naver_place_scraper.py
```

## Notes

- The function uses the same `clean_ai_briefing()` helper for consistent formatting
- Both Korean variations ("AI 브리핑" and "AI브리핑") are checked
- Maps URLs use the same `place_id` obtained from the initial search
- The feature is fully backward compatible - if Maps doesn't have it either, the result is the same as before (empty string)

## Future Improvements

Potential enhancements:
- Cache Maps responses to avoid redundant requests
- Add more Maps URL patterns if new structures are discovered
- Parallel checking of both sources for speed (if both exist, prefer Place)
- Configuration option to prefer Maps over Place
