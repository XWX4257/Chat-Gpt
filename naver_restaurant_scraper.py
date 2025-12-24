#!/usr/bin/env python3
"""
Naver Maps Restaurant Data Scraper

This script retrieves restaurant information from Naver Maps including:
- Place ID
- Visitor review count
- Blog review count
- Naver rating
- AI Briefing content
"""

import requests
import re
import json
from typing import Optional, Dict, Any
from urllib.parse import quote, urlparse, parse_qs
import time


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
        """
        Search for a restaurant on Naver Maps and retrieve its data.

        Args:
            restaurant_name: Name of the restaurant (e.g., "Namaste Wangsimni Branch")

        Returns:
            Dictionary containing restaurant data or None if not found
        """
        print(f"Searching for: {restaurant_name}")

        # Step 1: Search for the restaurant
        place_id = self._search_for_place_id(restaurant_name)
        if not place_id:
            print(f"Could not find place ID for '{restaurant_name}'")
            return None

        print(f"Found Place ID: {place_id}")

        # Step 2: Retrieve restaurant data
        restaurant_data = self._get_restaurant_data(place_id, restaurant_name)

        return restaurant_data

    def _search_for_place_id(self, restaurant_name: str) -> Optional[str]:
        """
        Search Naver Maps for a restaurant and extract its place ID.

        Args:
            restaurant_name: Name of the restaurant

        Returns:
            Place ID string or None if not found
        """
        try:
            # Search using Naver Maps search API
            search_url = f"https://map.naver.com/v5/search/{quote(restaurant_name)}"

            # Alternative: Use Naver search API
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

                # Extract place ID from search results
                if 'result' in data and 'place' in data['result']:
                    places = data['result']['place'].get('list', [])
                    if places:
                        # Return the first result's place ID
                        return places[0].get('id')

            # Fallback: Try to parse from the main search page
            response = self.session.get(search_url, timeout=10)
            if response.status_code == 200:
                # Look for place ID in the page content
                # Pattern: /place/ followed by numbers
                place_id_match = re.search(r'"id"\s*:\s*"(\d+)"', response.text)
                if place_id_match:
                    return place_id_match.group(1)

                # Alternative pattern
                place_id_match = re.search(r'/place/(\d+)', response.text)
                if place_id_match:
                    return place_id_match.group(1)

            return None

        except Exception as e:
            print(f"Error searching for place ID: {e}")
            return None

    def _get_restaurant_data(self, place_id: str, restaurant_name: str) -> Dict[str, Any]:
        """
        Retrieve detailed restaurant data using the place ID.

        Args:
            place_id: Naver Maps place ID
            restaurant_name: Name of the restaurant

        Returns:
            Dictionary containing restaurant data
        """
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
        """
        Fetch data from Naver Place API.

        Args:
            place_id: Naver Maps place ID
            data: Dictionary to update with fetched data
        """
        try:
            # Naver Place API endpoint
            api_url = f"https://pcmap-api.place.naver.com/place/info/basic/{place_id}"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': f'https://pcmap.place.naver.com/restaurant/{place_id}/home',
                'Accept': 'application/json, text/plain, */*'
            }

            response = self.session.get(api_url, headers=headers, timeout=10)

            if response.status_code == 200:
                result = response.json()

                # Extract review counts
                if 'visitorReviewCount' in result:
                    data['visitor_reviews'] = result['visitorReviewCount']

                if 'blogReviewCount' in result:
                    data['blog_reviews'] = result['blogReviewCount']

                # Extract rating
                if 'visitorReviewScore' in result:
                    data['naver_rating'] = result['visitorReviewScore']

                # Try to get AI briefing from the response
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
            print(f"Error fetching Place API data: {e}")

    def _fetch_maps_ai_briefing(self, place_id: str, data: Dict[str, Any]) -> None:
        """
        Fetch AI briefing from Naver Maps if not found in Place.

        Args:
            place_id: Naver Maps place ID
            data: Dictionary to update with AI briefing
        """
        try:
            # Try Naver Maps page
            maps_url = f"https://map.naver.com/v5/entry/place/{place_id}"
            response = self.session.get(maps_url, timeout=10)

            if response.status_code == 200:
                # Look for AI briefing in the page content
                ai_briefing_match = re.search(r'"aiBriefing"\s*:\s*"([^"]+)"', response.text)
                if ai_briefing_match:
                    data['ai_briefing'] = ai_briefing_match.group(1)
                else:
                    # Try alternative patterns
                    ai_briefing_match = re.search(r'AI 요약.*?<[^>]+>([^<]+)', response.text)
                    if ai_briefing_match:
                        data['ai_briefing'] = ai_briefing_match.group(1)

        except Exception as e:
            print(f"Error fetching Maps AI briefing: {e}")

    def display_results(self, data: Optional[Dict[str, Any]]) -> None:
        """
        Display the retrieved restaurant data in a formatted way.

        Args:
            data: Dictionary containing restaurant data
        """
        if not data:
            print("\nNo data found.")
            return

        print("\n" + "="*60)
        print(f"Restaurant: {data['restaurant_name']}")
        print("="*60)
        print(f"Place ID: {data['place_id']}")
        print(f"Naver Maps URL: {data['naver_maps_url']}")
        print(f"\nVisitor Reviews: {data['visitor_reviews'] if data['visitor_reviews'] is not None else 'N/A'}")
        print(f"Blog Reviews: {data['blog_reviews'] if data['blog_reviews'] is not None else 'N/A'}")
        print(f"Naver Rating: {data['naver_rating'] if data['naver_rating'] is not None else 'N/A'}")
        print(f"\nAI Briefing: {data['ai_briefing'] if data['ai_briefing'] else 'Not available'}")
        print("="*60)


def main():
    """Main function to run the scraper"""
    import sys

    # Get restaurant name from command line or use default
    if len(sys.argv) > 1:
        restaurant_name = ' '.join(sys.argv[1:])
    else:
        # Default example
        restaurant_name = "Namaste Wangsimni Branch"
        print(f"No restaurant name provided. Using example: {restaurant_name}")
        print("Usage: python naver_restaurant_scraper.py <restaurant name>")
        print()

    # Create scraper and search
    scraper = NaverRestaurantScraper()
    data = scraper.search_restaurant(restaurant_name)

    # Display results
    scraper.display_results(data)

    # Return data as JSON
    if data:
        print("\nJSON Output:")
        print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
