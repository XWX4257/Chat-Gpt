# Bug Fix: Review Keywords Extraction

## Problem
The `extract_review_keywords_robust()` function was failing to extract review keywords from the "이런 점이 좋았어요" (Good Points) section, returning empty results even though the data was visible on the page.

## Root Causes Identified

1. **Insufficient wait time** - Page content loads dynamically via JavaScript
2. **Limited parsing strategy** - Only used BeautifulSoup, which may miss dynamically loaded content
3. **Incorrect element selectors** - Naver's HTML structure may have changed or varies
4. **Timing issues** - Not waiting long enough after clicking expand buttons

## Solutions Implemented

### 1. **Multiple Extraction Strategies**
The new code uses **3 different strategies** in order of preference:

#### Strategy 1: Direct Selenium Search
- Searches for elements directly using multiple XPath selectors
- Tries different class patterns commonly used by Naver Place
- More reliable for JavaScript-rendered content
- Example selectors:
  ```python
  "//li[contains(@class, 'pui__')]//span"
  "//ul[contains(@class, 'pui__')]//li"
  "//div[contains(@class, 'place_section_content')]//li"
  ```

#### Strategy 2: BeautifulSoup with Section Detection
- First finds the keyword section by locating the header "이런 점이 좋았어요"
- Then parses only the relevant UL container
- Falls back to searching all LI elements if section not found
- Better parsing of text parts using `stripped_strings`

#### Strategy 3: Regex on Page Source
- Pattern matching for Korean keywords ending in "어요/해요" followed by numbers
- Fallback for when DOM parsing fails
- Pattern: `([가-힣\s]{3,30}[어해]요)[\s\n<>"]*(\d{1,5}(?:,\d{3})*)`

### 2. **Improved Wait Times**
```python
time.sleep(4)  # Increased from 3 for review page
time.sleep(2)  # Extra wait after expanding
time.sleep(1.5)  # After each expand click
```

### 3. **Better Expand Button Detection**
Now tries **multiple selectors** for the expand button:
```python
expand_selectors = [
    "//button[contains(text(), '펼쳐보기')]",
    "//a[contains(text(), '펼쳐보기')]",
    "//button[contains(text(), '더보기')]",
    "//a[contains(text(), '더보기')]",
    "//a[contains(@class, 'Tvx37')]",
    "//*[contains(@class, 'fvwqf')]"
]
```

### 4. **Enhanced Debugging**
Added `debug=True` parameter that:
- Shows which strategy is being used
- Displays how many elements were found
- Prints parsing progress
- Saves page source to `/tmp/debug_page_source.html` if all strategies fail
- Helps identify why extraction might fail

### 5. **Better Text Parsing**
- More robust number extraction with regex validation
- Filters out navigation menu items
- Handles multiple text formats
- Validates keyword length (2-60 characters)
- Removes HTML tags and normalizes whitespace

## Usage

### Basic Usage
```python
from naver_place_scraper import get_full_restaurant_data

data = get_full_restaurant_data("옥수동화덕피자", debug=True)
if data:
    print(data['keyword_stats'])
```

### Debug Mode
Enable debug output to see detailed extraction process:
```python
data = get_full_restaurant_data("옥수동화덕피자", debug=True)
```

Debug output shows:
- Which strategy successfully extracted keywords
- Number of elements found at each step
- Parsing details for troubleshooting

### If It Still Fails
1. Check `/tmp/debug_page_source.html` to see the actual HTML
2. Look for the keyword section in the HTML
3. Update selectors based on the actual structure
4. Increase wait times if content loads slowly

## Testing
Run the script:
```bash
python naver_place_scraper.py
```

Expected output should now include keywords like:
```
👍 Review Keywords (이런 점이 좋았어요):
   "음식이 맛있어요": 1,490
   "재료가 신선해요": 949
   ...
```

## Key Improvements Summary

| Issue | Old Approach | New Approach |
|-------|-------------|--------------|
| Element finding | Only BeautifulSoup | Selenium + BeautifulSoup + Regex |
| Wait time | 3 seconds | 4 seconds + extra waits |
| Expand button | Single selector | 6 different selectors |
| Debugging | None | Comprehensive debug mode |
| Fallbacks | 1 strategy | 3 independent strategies |

## Notes

- The script now tries multiple approaches, increasing the chance of success
- If one strategy fails, it automatically tries the next
- Debug mode helps diagnose issues quickly
- Page source is saved when all strategies fail for manual inspection
