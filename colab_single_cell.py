# ============================================================================
# NAVER RESTAURANT SCRAPER - GOOGLE COLAB SINGLE CELL VERSION
# ============================================================================
# Copy and paste this entire cell into Google Colab and run it!
# ============================================================================

# Install dependencies
!pip install requests -q

# Import libraries
import requests
import re
import json
from typing import Optional, Dict, Any
from urllib.parse import quote
from IPython.display import display, HTML, JSON
import pandas as pd


class NaverRestaurantScraper:
    """Scraper for Naver Maps/Place restaurant data"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://map.naver.com/'
        })

    def search_restaurant(self, restaurant_name: str) -> Optional[Dict[str, Any]]:
        """Search for a restaurant on Naver Maps and retrieve its data."""
        print(f"🔍 Searching for: {restaurant_name}")

        # Step 1: Search for the restaurant
        place_id = self._search_for_place_id(restaurant_name)
        if not place_id:
            print(f"❌ Could not find place ID for '{restaurant_name}'")
            return None

        print(f"✓ Found Place ID: {place_id}")

        # Step 2: Retrieve restaurant data
        restaurant_data = self._get_restaurant_data(place_id, restaurant_name)

        return restaurant_data

    def _search_for_place_id(self, restaurant_name: str) -> Optional[str]:
        """Search Naver Maps for a restaurant and extract its place ID."""
        try:
            # Search using Naver Maps search API
            api_search_url = "https://map.naver.com/v5/api/search"
            params = {
                'caller': 'pcweb',
                'query': restaurant_name,
                'type': 'all',
                'page': 1,
                'displayCount': 20,
                'isPlaceRecommendationReplace': 'true'
            }

            response = self.session.get(api_search_url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if 'result' in data and 'place' in data['result']:
                    places = data['result']['place'].get('list', [])
                    if places:
                        return places[0].get('id')

            # Fallback: Try to parse from the main search page
            search_url = f"https://map.naver.com/v5/search/{quote(restaurant_name)}"
            response = self.session.get(search_url, timeout=10)
            if response.status_code == 200:
                place_id_match = re.search(r'"id"\s*:\s*"(\d+)"', response.text)
                if place_id_match:
                    return place_id_match.group(1)
                place_id_match = re.search(r'/place/(\d+)', response.text)
                if place_id_match:
                    return place_id_match.group(1)

            return None

        except Exception as e:
            print(f"⚠️ Error searching for place ID: {e}")
            return None

    def _get_restaurant_data(self, place_id: str, restaurant_name: str) -> Dict[str, Any]:
        """Retrieve detailed restaurant data using the place ID."""
        data = {
            'restaurant_name': restaurant_name,
            'place_id': place_id,
            'naver_maps_url': f"https://map.naver.com/v5/entry/place/{place_id}",
            'visitor_reviews': None,
            'blog_reviews': None,
            'naver_rating': None,
            'ai_briefing': None
        }

        # Try to get data from Naver Place API
        self._fetch_place_api_data(place_id, data)

        # If no AI briefing found, try Naver Maps
        if not data['ai_briefing']:
            self._fetch_maps_ai_briefing(place_id, data)

        return data

    def _fetch_place_api_data(self, place_id: str, data: Dict[str, Any]) -> None:
        """Fetch data from Naver Place API."""
        try:
            api_url = f"https://pcmap-api.place.naver.com/place/info/basic/{place_id}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': f'https://pcmap.place.naver.com/restaurant/{place_id}/home',
                'Accept': 'application/json, text/plain, */*'
            }

            response = self.session.get(api_url, headers=headers, timeout=10)

            if response.status_code == 200:
                result = response.json()
                if 'visitorReviewCount' in result:
                    data['visitor_reviews'] = result['visitorReviewCount']
                if 'blogReviewCount' in result:
                    data['blog_reviews'] = result['blogReviewCount']
                if 'visitorReviewScore' in result:
                    data['naver_rating'] = result['visitorReviewScore']
                if 'aiBriefing' in result:
                    data['ai_briefing'] = result['aiBriefing']

            # Try additional API endpoint for AI briefing
            ai_briefing_url = f"https://pcmap-api.place.naver.com/place/info/ai-briefing/{place_id}"
            response = self.session.get(ai_briefing_url, headers=headers, timeout=10)

            if response.status_code == 200:
                result = response.json()
                if 'briefing' in result:
                    data['ai_briefing'] = result['briefing']
                elif 'content' in result:
                    data['ai_briefing'] = result['content']

        except Exception as e:
            print(f"⚠️ Error fetching Place API data: {e}")

    def _fetch_maps_ai_briefing(self, place_id: str, data: Dict[str, Any]) -> None:
        """Fetch AI briefing from Naver Maps if not found in Place."""
        try:
            maps_url = f"https://map.naver.com/v5/entry/place/{place_id}"
            response = self.session.get(maps_url, timeout=10)

            if response.status_code == 200:
                ai_briefing_match = re.search(r'"aiBriefing"\s*:\s*"([^"]+)"', response.text)
                if ai_briefing_match:
                    data['ai_briefing'] = ai_briefing_match.group(1)

        except Exception as e:
            print(f"⚠️ Error fetching Maps AI briefing: {e}")

    def display_results_colab(self, data: Optional[Dict[str, Any]]) -> None:
        """Display the retrieved restaurant data in a formatted way for Colab."""
        if not data:
            display(HTML('<h3 style="color: red;">❌ No data found.</h3>'))
            return

        # Create HTML display
        html = f"""
        <div style="border: 2px solid #4CAF50; border-radius: 10px; padding: 20px; background-color: #f9f9f9;">
            <h2 style="color: #4CAF50; margin-top: 0;">🍴 {data['restaurant_name']}</h2>
            <hr style="border: 1px solid #4CAF50;">

            <p><strong>📍 Place ID:</strong> <code>{data['place_id']}</code></p>
            <p><strong>🔗 Naver Maps URL:</strong> <a href="{data['naver_maps_url']}" target="_blank">{data['naver_maps_url']}</a></p>

            <hr style="border: 0.5px solid #ddd;">

            <h3>📊 Reviews & Ratings</h3>
            <ul>
                <li><strong>👥 Visitor Reviews:</strong> {data['visitor_reviews'] if data['visitor_reviews'] is not None else 'N/A'}</li>
                <li><strong>📝 Blog Reviews:</strong> {data['blog_reviews'] if data['blog_reviews'] is not None else 'N/A'}</li>
                <li><strong>⭐ Naver Rating:</strong> {data['naver_rating'] if data['naver_rating'] is not None else 'N/A'}</li>
            </ul>

            <hr style="border: 0.5px solid #ddd;">

            <h3>🤖 AI Briefing</h3>
            <p style="background-color: white; padding: 15px; border-radius: 5px; border-left: 4px solid #4CAF50;">
                {data['ai_briefing'] if data['ai_briefing'] else '<em style="color: #999;">Not available</em>'}
            </p>
        </div>
        """

        display(HTML(html))

        # Also display as DataFrame
        print("\n📋 Data Table:")
        df = pd.DataFrame([{
            'Restaurant': data['restaurant_name'],
            'Place ID': data['place_id'],
            'Visitor Reviews': data['visitor_reviews'],
            'Blog Reviews': data['blog_reviews'],
            'Rating': data['naver_rating']
        }])
        display(df)


# ============================================================================
# USAGE EXAMPLE - Modify the restaurant name below
# ============================================================================

# Enter restaurant name here
restaurant_name = "Namaste Wangsimni Branch"  # ← Change this!

# Create scraper and search
scraper = NaverRestaurantScraper()
data = scraper.search_restaurant(restaurant_name)

# Display results
if data:
    scraper.display_results_colab(data)

    # Also show JSON output
    print("\n" + "="*60)
    print("📄 JSON Output:")
    print("="*60)
    print(json.dumps(data, ensure_ascii=False, indent=2))
else:
    print("❌ Restaurant not found. Please try a different name.")
