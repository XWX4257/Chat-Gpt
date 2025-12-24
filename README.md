# Naver Restaurant Data Scraper

A Python tool to retrieve restaurant information from Naver Maps and Naver Place, including reviews, ratings, and AI-generated briefings.

## Features

- **Restaurant Search**: Find restaurants on Naver Maps by name
- **Place ID Extraction**: Automatically extract the unique place ID from Naver Maps URLs
- **Review Counts**: Retrieve both visitor review and blog review counts
- **Ratings**: Get Naver rating scores (when available)
- **AI Briefing**: Extract AI-generated briefing content from Naver Place or Naver Maps

## Installation

### Option 1: Google Colab (No Installation Required!) ⭐

The easiest way to use this scraper is with Google Colab:

1. **Upload Notebook**: Go to [Google Colab](https://colab.research.google.com/) and upload `naver_restaurant_scraper_colab.ipynb`
2. **Or Copy-Paste**: Copy the content from `colab_single_cell.py` into a Colab cell
3. **Run**: Execute the cells and get results instantly!

📖 See [COLAB_USAGE.md](COLAB_USAGE.md) for detailed Colab instructions.

### Option 2: Local Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Google Colab (Recommended for Beginners)

```python
# In Google Colab, just run this in a single cell:
!pip install requests -q

# Then copy the scraper code and use it:
restaurant_name = "Namaste Wangsimni Branch"
scraper = NaverRestaurantScraper()
data = scraper.search_restaurant(restaurant_name)
scraper.display_results_colab(data)
```

See [COLAB_USAGE.md](COLAB_USAGE.md) for complete examples.

### Command Line

Run the scraper with a restaurant name:

```bash
python naver_restaurant_scraper.py "Namaste Wangsimni Branch"
```

Or run without arguments to use the default example:

```bash
python naver_restaurant_scraper.py
```

### Python Module

You can also use it as a Python module:

```python
from naver_restaurant_scraper import NaverRestaurantScraper

# Create scraper instance
scraper = NaverRestaurantScraper()

# Search for a restaurant
data = scraper.search_restaurant("Namaste Wangsimni Branch")

# Display results
scraper.display_results(data)

# Access individual fields
if data:
    print(f"Place ID: {data['place_id']}")
    print(f"Visitor Reviews: {data['visitor_reviews']}")
    print(f"Blog Reviews: {data['blog_reviews']}")
    print(f"Naver Rating: {data['naver_rating']}")
    print(f"AI Briefing: {data['ai_briefing']}")
```

## Output Format

The scraper returns a dictionary with the following structure:

```json
{
  "restaurant_name": "Namaste Wangsimni Branch",
  "place_id": "1234567890",
  "naver_maps_url": "https://map.naver.com/v5/entry/place/1234567890",
  "visitor_reviews": 150,
  "blog_reviews": 45,
  "naver_rating": 4.5,
  "ai_briefing": "AI-generated summary of the restaurant..."
}
```

## How It Works

1. **Search Phase**:
   - Queries Naver Maps search API with the restaurant name
   - Extracts the place ID from search results

2. **Data Retrieval Phase**:
   - Uses Naver Place API to fetch review counts and ratings
   - Retrieves AI briefing from Naver Place API

3. **Fallback Phase**:
   - If AI briefing is not found in Naver Place, searches Naver Maps
   - Parses the page content to extract AI briefing

## Data Fields

- **restaurant_name**: The input restaurant name
- **place_id**: Unique identifier for the restaurant on Naver Maps
- **naver_maps_url**: Direct URL to the restaurant's Naver Maps page
- **visitor_reviews**: Number of visitor reviews (user reviews)
- **blog_reviews**: Number of blog posts reviewing the restaurant
- **naver_rating**: Average rating score (may be `None` if not available)
- **ai_briefing**: AI-generated summary/briefing (may be `None` if not available)

## Requirements

- Python 3.6+
- requests library

## Notes

- The scraper respects Naver's website structure and uses appropriate headers
- Some restaurants may not have all data fields available
- AI Briefing may not be available for all restaurants
- Network timeout is set to 10 seconds per request

## Example Output

```
Searching for: Namaste Wangsimni Branch
Found Place ID: 1234567890

============================================================
Restaurant: Namaste Wangsimni Branch
============================================================
Place ID: 1234567890
Naver Maps URL: https://map.naver.com/v5/entry/place/1234567890

Visitor Reviews: 150
Blog Reviews: 45
Naver Rating: 4.5

AI Briefing: Popular Indian restaurant known for authentic flavors...
============================================================
```

## License

MIT License
