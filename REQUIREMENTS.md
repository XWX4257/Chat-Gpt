# Naver Restaurant Scraper - Requirements

## Exact Execution Flow

The scraper follows this precise sequence:

### Step 1: Input
- Take restaurant name as input (e.g., "Namaste Wangsimni Branch", "디핀옥수")

### Step 2: Get Naver Place URL and Place ID
- Retrieve the restaurant's Naver Place URL using the restaurant name
- Extract the Place ID from the URL

### Step 3: Fetch Review Counts
- Using the Place ID, fetch the number of **visitor reviews**
- Using the Place ID, fetch the number of **blog reviews**

### Step 4: Fetch Naver Rating (Optional)
- Retrieve the Naver rating
- If no Naver rating is available, it may be omitted from the results

### Step 5: Fetch AI Briefing (Priority Order)
1. **First**: Check the restaurant's Naver Place page for an AI Briefing
2. **If not found**: Search for the restaurant on Naver Maps and check whether an AI Briefing is available there
3. **If exists**: Retrieve it

## Data Output

The scraper returns a dictionary with the following structure:

```json
{
  "restaurant_name": "디핀옥수",
  "place_id": "1234567890",
  "naver_place_url": "https://m.place.naver.com/restaurant/1234567890/home",
  "naver_maps_url": "https://map.naver.com/v5/entry/place/1234567890",
  "visitor_reviews": 150,
  "blog_reviews": 45,
  "naver_rating": 4.5,
  "ai_briefing": "AI-generated restaurant summary..."
}
```

## Field Descriptions

| Field | Description | Required |
|-------|-------------|----------|
| `restaurant_name` | Input restaurant name | Yes |
| `place_id` | Naver Maps unique place identifier | Yes |
| `naver_place_url` | Direct URL to Naver Place page | Yes |
| `naver_maps_url` | Direct URL to Naver Maps page | Yes |
| `visitor_reviews` | Number of visitor reviews (방문자리뷰) | Yes |
| `blog_reviews` | Number of blog reviews (블로그리뷰) | Yes |
| `naver_rating` | Average rating score (0-5) | No (optional) |
| `ai_briefing` | AI-generated summary text | No (optional) |

## Optional Fields

- **Naver Rating**: May be `null` if not available for the restaurant
- **AI Briefing**: May be `null` if not found on either Naver Place or Naver Maps

## Search Priority

### AI Briefing Search Order:
1. ✅ **Naver Place** (checked first)
2. ✅ **Naver Maps** (fallback if not found on Naver Place)

If AI Briefing is not found on either platform, the field will be `null`.

## Implementation Details

### Step 1: Search & URL Retrieval
```python
# Search Naver Maps for restaurant
search_url = f"https://map.naver.com/v5/search/{restaurant_name}"

# Extract Place ID from results
place_id = extract_from_url_or_page()

# Construct Naver Place URL
naver_place_url = f"https://m.place.naver.com/restaurant/{place_id}/home"
```

### Step 2: Review Count Extraction
```python
# Navigate to Naver Place URL
visit(naver_place_url)

# Extract visitor reviews
visitor_reviews = find_element_with_text("방문자리뷰")

# Extract blog reviews
blog_reviews = find_element_with_text("블로그리뷰")
```

### Step 3: Rating Extraction
```python
# On Naver Place page
naver_rating = find_rating_score()

# If not found, set to None (optional field)
if not naver_rating:
    naver_rating = None
```

### Step 4: AI Briefing Extraction (Priority Order)
```python
# Priority 1: Check Naver Place
ai_briefing = find_ai_briefing_on_place()

if not ai_briefing:
    # Priority 2: Check Naver Maps
    visit(f"https://map.naver.com/v5/entry/place/{place_id}")
    ai_briefing = find_ai_briefing_on_maps()

# If still not found, set to None
if not ai_briefing:
    ai_briefing = None
```

## Error Handling

### Restaurant Not Found
If the restaurant cannot be found:
```python
return None
```

### Missing Data
For optional fields that cannot be found:
- `naver_rating`: Set to `None`
- `ai_briefing`: Set to `None`

### Required Data
If required data cannot be retrieved:
- `place_id`: Return `None` for entire result
- `visitor_reviews`: Set to `None` but continue
- `blog_reviews`: Set to `None` but continue

## Example Usage

```python
# Input
restaurant_name = "디핀옥수"

# Execute scraper
scraper = NaverRestaurantScraper()
data = scraper.search_restaurant(restaurant_name)

# Output
{
  "restaurant_name": "디핀옥수",
  "place_id": "1672120714",
  "naver_place_url": "https://m.place.naver.com/restaurant/1672120714/home",
  "naver_maps_url": "https://map.naver.com/v5/entry/place/1672120714",
  "visitor_reviews": 234,
  "blog_reviews": 89,
  "naver_rating": 4.3,
  "ai_briefing": "옥수동에 위치한 일식당..."
}
```

## Validation Rules

1. **Place ID**: Must be numeric, 5-20 digits
2. **Review Counts**: Must be non-negative integers or `None`
3. **Rating**: Must be float between 0-5 or `None`
4. **AI Briefing**: Must be string with length > 10 characters or `None`

## Success Criteria

A successful scrape must include:
- ✅ Restaurant name (input)
- ✅ Place ID (extracted)
- ✅ Naver Place URL (constructed)
- ✅ Naver Maps URL (constructed)
- ✅ Visitor reviews (extracted or None)
- ✅ Blog reviews (extracted or None)
- Optional: Naver rating
- Optional: AI Briefing (checked in priority order)
