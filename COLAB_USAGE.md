# Google Colab Usage Guide

This guide shows you how to run the Naver Restaurant Scraper in Google Colab.

## Option 1: Upload the Notebook (Recommended)

1. Go to [Google Colab](https://colab.research.google.com/)
2. Click **File** → **Upload notebook**
3. Upload `naver_restaurant_scraper_colab.ipynb`
4. Run each cell sequentially
5. Modify the restaurant name in Step 3
6. Get beautiful formatted results!

## Option 2: Single Cell - Copy & Paste

1. Go to [Google Colab](https://colab.research.google.com/)
2. Create a new notebook
3. Copy the entire content from `colab_single_cell.py`
4. Paste it into a single cell
5. Run the cell
6. Done! 🎉

## Option 3: Direct GitHub Upload

1. Go to [Google Colab](https://colab.research.google.com/)
2. Click **File** → **Open notebook**
3. Select **GitHub** tab
4. Enter: `XWX4257/Chat-Gpt`
5. Select the notebook file
6. Run!

## Quick Start Example

### Single Cell Version

```python
# Just copy this entire block into a Colab cell and run!

!pip install requests -q

import requests
import re
import json
from typing import Optional, Dict, Any
from urllib.parse import quote
from IPython.display import display, HTML
import pandas as pd

# [Paste the rest of colab_single_cell.py here]

# Change restaurant name below
restaurant_name = "Namaste Wangsimni Branch"
scraper = NaverRestaurantScraper()
data = scraper.search_restaurant(restaurant_name)

if data:
    scraper.display_results_colab(data)
```

## Features in Colab

✅ **Beautiful HTML Display** - Color-coded results with emojis
✅ **Pandas DataFrames** - Tabular view of data
✅ **Interactive JSON Viewer** - Expandable JSON output
✅ **Download Results** - Save as JSON file
✅ **Batch Processing** - Search multiple restaurants
✅ **No Installation Required** - Runs entirely in the browser

## Example Outputs

### Single Restaurant Search
```python
restaurant_name = "Namaste Wangsimni Branch"
scraper = NaverRestaurantScraper()
data = scraper.search_restaurant(restaurant_name)
scraper.display_results_colab(data)
```

### Multiple Restaurants
```python
restaurants = [
    "Namaste Wangsimni Branch",
    "신당동 떡볶이",
    "광장시장 마약김밥"
]

scraper = NaverRestaurantScraper()
for name in restaurants:
    data = scraper.search_restaurant(name)
    if data:
        scraper.display_results_colab(data)
```

### Get JSON Output
```python
if data:
    print(json.dumps(data, ensure_ascii=False, indent=2))
```

### Download as File
```python
from google.colab import files

filename = f"{data['place_id']}_data.json"
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

files.download(filename)
```

## Troubleshooting

### Import Error
- Make sure to run the installation cell first: `!pip install requests -q`

### Restaurant Not Found
- Try using the exact name as it appears on Naver Maps
- Include branch names if applicable (e.g., "Wangsimni Branch")
- Try Korean name if available

### Timeout Errors
- The scraper has a 10-second timeout per request
- If you get timeout errors, wait a moment and try again

### No AI Briefing
- Not all restaurants have AI Briefing
- The field will show "Not available" if missing
- Other data (reviews, ratings) will still be retrieved

## Advanced Usage

### Custom Search with Error Handling
```python
def safe_search(restaurant_name):
    try:
        scraper = NaverRestaurantScraper()
        data = scraper.search_restaurant(restaurant_name)
        if data:
            return data
        else:
            print(f"Could not find: {restaurant_name}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

# Use it
data = safe_search("Your Restaurant Name")
```

### Save Multiple Results to CSV
```python
import pandas as pd

restaurants = ["Restaurant 1", "Restaurant 2", "Restaurant 3"]
scraper = NaverRestaurantScraper()

results = []
for name in restaurants:
    data = scraper.search_restaurant(name)
    if data:
        results.append(data)

# Create DataFrame and save
df = pd.DataFrame(results)
df.to_csv('restaurants.csv', index=False, encoding='utf-8-sig')

# Download in Colab
from google.colab import files
files.download('restaurants.csv')
```

## Requirements

- Google account (for Colab access)
- Internet connection
- No local Python installation needed!

## Data Fields Returned

| Field | Description | Type |
|-------|-------------|------|
| `restaurant_name` | Name of the restaurant | String |
| `place_id` | Naver Maps unique ID | String |
| `naver_maps_url` | Direct URL to restaurant page | String |
| `visitor_reviews` | Number of visitor reviews | Integer or None |
| `blog_reviews` | Number of blog reviews | Integer or None |
| `naver_rating` | Average rating score | Float or None |
| `ai_briefing` | AI-generated summary | String or None |

## Tips for Best Results

1. **Use Exact Names**: Copy the restaurant name exactly from Naver Maps
2. **Include Location**: Add branch/location info (e.g., "Gangnam Branch")
3. **Korean Names**: Korean names often work better than English
4. **Check Output**: Always verify the Place ID matches your intended restaurant

## Support

If you encounter issues:
1. Check the Troubleshooting section above
2. Verify your internet connection
3. Make sure the restaurant exists on Naver Maps
4. Try searching with different name variations

## License

MIT License - Free to use and modify!
