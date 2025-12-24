# Keyword Extraction Bug Fix - Summary

## Problem Identified

The debug output showed:
```
[DEBUG] LI parts: ['업체']
[DEBUG] LI parts: ['클립']
[DEBUG] LI parts: ['내부']
...
```

These are **navigation/menu items**, NOT the actual review keywords. The code was finding the wrong `<ul>` section on the page.

## Root Cause

The original code:
1. Found the "이런 점이 좋았어요" header
2. Went up the parent tree and grabbed the FIRST `<ul>` it found
3. That `<ul>` was actually a navigation menu or photo gallery labels

The actual keyword section with items like "음식이 맛있어요 1,490" was in a different `<ul>` element.

## Solution Implemented

### 1. Section Validation
Now validates EACH `<ul>` section before parsing:
```python
# Check if this UL has keyword-like items
has_numbers = re.search(r'\d{2,}', sample_text)  # Has numbers with 2+ digits
has_korean_endings = re.search(r'[어해]요', sample_text)  # Has Korean verb endings

if has_numbers and has_korean_endings:
    keyword_section = ul_section  # This is the right section!
```

### 2. Better Scrolling
```python
# Try multiple scroll positions
for scroll_pos in [400, 800, 1200, 1600, 2000]:
    driver.execute_script(f"window.scrollTo(0, {scroll_pos});")
    # Check if keyword section is now visible
```

### 3. Aria-Label Pattern Recognition
Added support for accessibility labels:
```python
# Pattern: "음식이 맛있어요 이 키워드를 선택한 인원 1490명"
match = re.search(r'(.+?)\s*이 키워드를 선택한 인원\s*(\d+(?:,\d+)*)', line)
```

### 4. Navigation Item Filtering
```python
ignore_list = ["홈", "메뉴", "리뷰", "사진", "지도", "주변", "예약", "주문",
               "방문자 리뷰", "블로그 리뷰", "영수증", "이런 점이 좋았어요",
               "업체", "클립", "내부", "외부", "동영상", "방문자", "블로그"]
```

### 5. Enhanced XPath Selectors
```python
keyword_selectors = [
    "//li[contains(., '어요') and contains(., '이 키워드를 선택한 인원')]",
    "//li[contains(., '해요') and contains(., '이 키워드를 선택한 인원')]",
    "//li[contains(@class, 'pui__') and (contains(., '어요') or contains(., '해요'))]",
    ...
]
```

## What Changed

| Before | After |
|--------|-------|
| Found first `<ul>`, got wrong section | Validates each `<ul>` for keyword patterns |
| Single scroll position | Multiple scroll positions (5 attempts) |
| Generic selectors | Specific selectors for keyword items |
| No aria-label support | Extracts from aria-label patterns |
| Basic filtering | Comprehensive navigation item filtering |
| Silent failures | Debug output shows which keywords found |

## Testing the Fix

### Run the Script
```bash
python /home/user/Chat-Gpt/naver_place_scraper.py
```

### Expected Output
You should now see:
```
[DEBUG] Found valid keyword UL with XX LI elements
[DEBUG] Found keyword: 음식이 맛있어요 = 1490
[DEBUG] Found keyword: 재료가 신선해요 = 949
...
✓ Found XX distinct keyword items

👍 Review Keywords (이런 점이 좋았어요):
   "음식이 맛있어요": 1,490
   "재료가 신선해요": 949
   ...
```

### If It Still Fails

The script saves the page HTML to `/tmp/debug_page_source.html`. You can:

1. **Check the saved HTML file:**
   ```bash
   grep -A 5 "이런 점이 좋았어요" /tmp/debug_page_source.html
   ```

2. **Look for the keyword pattern in HTML:**
   ```bash
   grep -E "어요.*[0-9]{2,}" /tmp/debug_page_source.html | head -20
   ```

3. **Send me the HTML snippet** containing the keyword section so I can adjust the selectors

## Key Improvements

✅ **Smart Section Detection** - Only parses sections that look like keyword lists
✅ **Multiple Scroll Attempts** - Ensures keyword section is visible
✅ **Aria-Label Support** - Works with accessibility attributes
✅ **Better Filtering** - Excludes navigation and menu items
✅ **Debug Visibility** - Shows exactly which keywords are found

## Next Steps

1. Run the updated script
2. Check if keywords are now extracted correctly
3. If you still see "(No keyword stats found)", share the debug output and I'll investigate further

The fix is comprehensive and should handle the issue, but Naver's HTML structure can vary, so additional adjustments may be needed based on the actual page structure.
