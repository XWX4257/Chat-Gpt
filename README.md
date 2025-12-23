# Naver Place Review Crawler

A Python-based web crawler to extract review statistics from Naver Place restaurant pages. Compatible with Google Colab.

## Features

Crawls and extracts:
- Total number of reviews
- Total number of visitor reviews
- Total number of blog reviews

## Files

- `naver_place_crawler.py` - Standalone Python script
- `naver_place_crawler.ipynb` - Google Colab notebook (recommended)
- `requirements.txt` - Python dependencies

## Quick Start (Google Colab)

### Method 1: Upload Notebook to Colab

1. Go to [Google Colab](https://colab.research.google.com/)
2. Click "File" → "Upload notebook"
3. Upload `naver_place_crawler.ipynb`
4. Run all cells in order

### Method 2: Open from GitHub

1. Go to [Google Colab](https://colab.research.google.com/)
2. Click "File" → "Open notebook" → "GitHub" tab
3. Enter this repository URL
4. Select `naver_place_crawler.ipynb`
5. Run all cells in order

## Usage

### In Google Colab

Simply run all cells in the notebook. The notebook will:
1. Install required packages (Selenium, Chrome driver)
2. Set up the crawler
3. Crawl the target URL
4. Display results

### Standalone Python Script

```bash
# Install dependencies
pip install -r requirements.txt

# Install Chrome driver (for local use)
# On Ubuntu/Debian:
sudo apt-get install chromium-chromedriver

# On macOS:
brew install chromedriver

# Run the script
python naver_place_crawler.py
```

## Example Output

```
============================================================
Naver Place Review Crawler
============================================================
Accessing URL: https://m.place.naver.com/restaurant/1672120714/review/visitor
Visitor tab text: 방문자리뷰 1,234
Blog tab text: 블로그리뷰 567

============================================================
RESULTS
============================================================
URL: https://m.place.naver.com/restaurant/1672120714/review/visitor
Total Reviews: 1,801
Visitor Reviews: 1,234
Blog Reviews: 567
============================================================
```

## Customization

### Crawl Different URLs

Edit the URL in the script or notebook:

```python
url = "https://m.place.naver.com/restaurant/YOUR_RESTAURANT_ID/review/visitor"
results = crawl_naver_place_reviews(url)
```

### Crawl Multiple Restaurants

Use the "Optional: Crawl Multiple URLs" cell in the notebook or modify the script to loop through multiple URLs.

## Technical Details

- Uses Selenium WebDriver for browser automation
- Configured for headless Chrome
- Mobile user-agent for accessing mobile Naver pages
- XPath selectors to find review count elements
- Regex patterns to extract numbers from Korean text

## Troubleshooting

**Issue: No review counts found**
- Naver may have changed their page structure
- Check the debug output showing page source
- Adjust XPath selectors if needed

**Issue: Chrome driver not found**
- Make sure Chrome/Chromium is installed
- Run the installation commands in the notebook

**Issue: Timeout errors**
- Increase the wait time in the script
- Check your internet connection

## Requirements

- Python 3.7+
- Selenium 4.0+
- Chrome/Chromium browser
- ChromeDriver

## Notes

- This crawler is for educational purposes
- Be respectful of Naver's servers (add delays between requests)
- Naver's page structure may change over time, requiring updates to selectors

## License

MIT
