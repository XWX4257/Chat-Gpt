# Naver Restaurant Scraper - Selenium Version

## Why Selenium?

The **Selenium version** is **recommended** because:

- ✅ **Handles JavaScript**: Naver Maps loads content dynamically with JavaScript
- ✅ **More Reliable**: Works with Korean restaurant names like "디핀옥수"
- ✅ **Complete Data**: Can access all review counts, ratings, and AI briefings
- ✅ **Works in Colab**: Specifically designed for Google Colab environment

The original `requests`-based version may fail because it cannot execute JavaScript that Naver uses to load restaurant data.

## Quick Start (Google Colab)

### Option 1: Single Cell - Copy & Paste

1. Open [Google Colab](https://colab.research.google.com/)
2. Create a new notebook
3. Copy the entire content of `colab_selenium_complete.py`
4. Paste into a single cell
5. Modify the restaurant name (line near the bottom)
6. Run the cell (Shift + Enter)
7. Wait 30-60 seconds for installation and scraping
8. Get results! 🎉

### Option 2: Upload Standalone Script

1. Upload `naver_restaurant_scraper_selenium.py` to Colab
2. Run installation commands:
```python
!apt-get update -qq
!apt-get install -y wget unzip -qq
!wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
!apt-get install -y ./google-chrome-stable_current_amd64.deb -qq
!pip install -q webdriver-manager selenium
```
3. Use the scraper:
```python
from naver_restaurant_scraper_selenium import NaverRestaurantScraperSelenium

scraper = NaverRestaurantScraperSelenium()
data = scraper.search_restaurant("디핀옥수")
scraper.display_results(data)
```

## Features

### Complete Data Extraction

- **Place ID**: Unique identifier for the restaurant
- **Visitor Reviews**: Number of visitor reviews (방문자리뷰)
- **Blog Reviews**: Number of blog posts about the restaurant (블로그리뷰)
- **Naver Rating**: Average rating score (별점)
- **AI Briefing**: AI-generated summary of the restaurant

### Multi-Method Search

The scraper uses 3 different methods to find restaurant data:

1. **URL Redirect**: Checks if search redirects directly to place page
2. **Search Results**: Scans all links in search results
3. **Page Source**: Parses HTML source for place ID patterns

### Robust Error Handling

- Graceful failure with helpful error messages
- Automatic driver cleanup
- Timeout protection
- Detailed logging

## Usage Examples

### Example 1: Basic Search

```python
scraper = NaverRestaurantScraper()
data = scraper.search_restaurant("디핀옥수")

if data:
    print(f"Place ID: {data['place_id']}")
    print(f"Visitor Reviews: {data['visitor_reviews']}")
    print(f"Blog Reviews: {data['blog_reviews']}")
    print(f"Rating: {data['naver_rating']}")
    print(f"AI Briefing: {data['ai_briefing']}")
```

### Example 2: Multiple Restaurants

```python
restaurants = ["디핀옥수", "신당동 떡볶이", "광장시장 마약김밥"]

for name in restaurants:
    scraper = NaverRestaurantScraper()
    data = scraper.search_restaurant(name)
    if data:
        scraper.display_results_colab(data)
    print("\n" + "="*60 + "\n")
```

### Example 3: Save to JSON

```python
import json

scraper = NaverRestaurantScraper()
data = scraper.search_restaurant("디핀옥수")

if data:
    # Save to file
    with open('restaurant_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Download in Colab
    from google.colab import files
    files.download('restaurant_data.json')
```

## Installation (Local Use)

If you want to run locally (not in Colab):

```bash
# Install Chrome
# On Ubuntu/Debian:
sudo apt-get update
sudo apt-get install -y google-chrome-stable

# On macOS:
brew install --cask google-chrome

# On Windows:
# Download from https://www.google.com/chrome/

# Install Python packages
pip install selenium webdriver-manager
```

Then run:

```bash
python naver_restaurant_scraper_selenium.py "디핀옥수"
```

## Comparison: Requests vs Selenium

| Feature | Requests Version | Selenium Version |
|---------|-----------------|------------------|
| JavaScript Support | ❌ No | ✅ Yes |
| Speed | ⚡ Fast (2-3s) | 🐢 Slower (10-15s) |
| Reliability | ⚠️ May fail | ✅ High |
| Setup Complexity | ✅ Simple | ⚠️ Moderate |
| Google Colab | ❌ May fail | ✅ Works great |
| Korean Names | ❌ Often fails | ✅ Works well |
| **Recommended** | For simple testing | **For production use** |

## Troubleshooting

### Issue: ChromeDriver version mismatch

**Solution**: The code uses `webdriver-manager` which automatically downloads the correct ChromeDriver version. If you still have issues:

```python
!pip install --upgrade webdriver-manager
```

### Issue: "chrome not reachable"

**Solution**: This is normal in Colab when the driver is cleaning up. Ignore this message if you got results.

### Issue: Restaurant not found

**Solutions**:
1. Try the exact name as shown on Naver Maps
2. Include location/branch info (e.g., "강남점")
3. Try both Korean and English names
4. Check spelling carefully

### Issue: No review data

**Reasons**:
- Restaurant may be very new
- Naver may have changed their page structure
- Restaurant may not have reviews yet

**Solution**: Check the URLs manually to verify the data exists on Naver.

## Performance Tips

1. **Reuse Driver**: If searching multiple restaurants, reuse the driver:
```python
scraper = NaverRestaurantScraper()
scraper.driver = scraper.setup_driver()

for name in restaurants:
    data = scraper.search_restaurant(name)
    # Process data...

scraper.driver.quit()
```

2. **Adjust Timeouts**: Modify sleep times if your connection is slow:
```python
# In the code, change:
time.sleep(3)  # Increase to 5 or more
```

3. **Headless Mode**: Already enabled by default for better performance in Colab

## Technical Details

### Chrome Options Used

- `--headless`: Runs without GUI (required for Colab)
- `--no-sandbox`: Disables sandboxing (required for Colab)
- `--disable-dev-shm-usage`: Uses /tmp instead of /dev/shm
- `--disable-gpu`: Disables GPU acceleration
- `--window-size=1920,1080`: Sets viewport size
- `--user-agent`: Sets browser user agent
- `--lang=ko-KR`: Sets Korean language

### XPath Selectors

The scraper uses XPath to find elements:
- `//*[contains(text(), '방문자리뷰')]` - Finds visitor review text
- `//*[contains(text(), '블로그리뷰')]` - Finds blog review text
- `//*[contains(@class, 'score')]//em` - Finds rating score

### Data Extraction Flow

```
1. User provides restaurant name
   ↓
2. Search on Naver Maps
   ↓
3. Extract Place ID (3 methods)
   ↓
4. Navigate to mobile Naver Place
   ↓
5. Extract data using XPath
   ↓
6. Return structured JSON
```

## License

MIT License - Free to use and modify!

## Credits

Based on Selenium WebDriver and inspired by best practices for web scraping in Google Colab.

## Support

If you encounter issues:
1. Check this README for troubleshooting
2. Verify Chrome is installed correctly
3. Check your internet connection
4. Ensure the restaurant exists on Naver Maps
