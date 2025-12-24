#!/usr/bin/env python3
"""
Naver Restaurant Scraper - Selenium Version for Google Colab

This version uses Selenium with Chrome WebDriver to handle JavaScript-rendered content.
Works perfectly in Google Colab!
"""

import re
import time
import json
from typing import Optional, Dict, Any
from urllib.parse import quote


class NaverRestaurantScraperSelenium:
    """Selenium-based scraper for Naver Maps/Place restaurant data"""

    def __init__(self, driver=None):
        """
        Initialize scraper with optional pre-configured driver.

        Args:
            driver: Optional pre-configured Selenium WebDriver
        """
        self.driver = driver
        self.driver_owned = False if driver else True

    def setup_driver(self):
        """Set up Chrome driver with options suitable for Colab"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
        except ImportError:
            raise ImportError(
                "Selenium not installed. Run: pip install selenium webdriver-manager"
            )

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--lang=ko-KR')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    def extract_number(self, text):
        """Extract number from text, handling Korean formatting with commas"""
        if not text:
            return None
        match = re.search(r'(\d+(?:,\d+)*)', text)
        if match:
            return int(match.group(1).replace(',', ''))
        return None

    def search_restaurant(self, restaurant_name: str) -> Optional[Dict[str, Any]]:
        """
        Search for a restaurant on Naver Maps and retrieve its data.

        Args:
            restaurant_name: Name of the restaurant

        Returns:
            Dictionary containing restaurant data or None if not found
        """
        print(f"🔍 Searching for: {restaurant_name}")

        # Set up driver if not already done
        if not self.driver:
            print("Setting up Chrome WebDriver...")
            self.driver = self.setup_driver()
            self.driver_owned = True

        try:
            # Step 1: Search for the restaurant and get place ID
            place_id = self._search_for_place_id(restaurant_name)
            if not place_id:
                print(f"❌ Could not find place ID for '{restaurant_name}'")
                return None

            print(f"✓ Found Place ID: {place_id}")

            # Step 2: Retrieve restaurant data
            restaurant_data = self._get_restaurant_data(place_id, restaurant_name)

            return restaurant_data

        finally:
            # Clean up driver if we own it
            if self.driver_owned and self.driver:
                self.driver.quit()
                self.driver = None

    def _search_for_place_id(self, restaurant_name: str) -> Optional[str]:
        """
        Search Naver Maps for a restaurant and extract its place ID using Selenium.

        Args:
            restaurant_name: Name of the restaurant

        Returns:
            Place ID string or None if not found
        """
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            # Navigate to Naver Maps search
            search_url = f"https://map.naver.com/v5/search/{quote(restaurant_name)}"
            print(f"Accessing: {search_url}")
            self.driver.get(search_url)

            # Wait for page to load
            time.sleep(3)

            # Try to find place ID in various ways
            place_id = None

            # Method 1: Look in URL if redirected to place page
            current_url = self.driver.current_url
            place_match = re.search(r'/place/(\d+)', current_url)
            if place_match:
                place_id = place_match.group(1)
                print(f"✓ Found place ID in URL: {place_id}")
                return place_id

            # Method 2: Look for place links in search results
            try:
                wait = WebDriverWait(self.driver, 10)
                # Wait for search results to appear
                wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'place') or contains(@class, 'search')]")))
                time.sleep(2)

                # Find all links that might contain place IDs
                links = self.driver.find_elements(By.TAG_NAME, "a")
                for link in links:
                    href = link.get_attribute("href")
                    if href and '/place/' in href:
                        match = re.search(r'/place/(\d+)', href)
                        if match:
                            place_id = match.group(1)
                            print(f"✓ Found place ID in search results: {place_id}")
                            return place_id
            except:
                pass

            # Method 3: Check page source for place ID patterns
            page_source = self.driver.page_source
            patterns = [
                r'"id"\s*:\s*"(\d+)"',
                r'"placeId"\s*:\s*"(\d+)"',
                r'/place/(\d+)',
                r'place\?id=(\d+)',
            ]

            for pattern in patterns:
                matches = re.findall(pattern, page_source)
                if matches:
                    # Get the first valid place ID (numeric, reasonable length)
                    for match in matches:
                        if match.isdigit() and 5 <= len(match) <= 20:
                            place_id = match
                            print(f"✓ Found place ID in page source: {place_id}")
                            return place_id

            return place_id

        except Exception as e:
            print(f"⚠️ Error searching for place ID: {e}")
            import traceback
            traceback.print_exc()
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
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        data = {
            'restaurant_name': restaurant_name,
            'place_id': place_id,
            'naver_maps_url': f"https://map.naver.com/v5/entry/place/{place_id}",
            'naver_place_url': f"https://m.place.naver.com/restaurant/{place_id}/home",
            'visitor_reviews': None,
            'blog_reviews': None,
            'naver_rating': None,
            'ai_briefing': None
        }

        # Try mobile Naver Place page (usually has better structured data)
        mobile_url = f"https://m.place.naver.com/restaurant/{place_id}/home"
        print(f"Accessing mobile page: {mobile_url}")

        try:
            self.driver.get(mobile_url)
            time.sleep(3)

            wait = WebDriverWait(self.driver, 10)

            # Extract visitor reviews
            try:
                # Look for visitor review tab/link
                visitor_elements = self.driver.find_elements(By.XPATH,
                    "//*[contains(text(), '방문자리뷰') or contains(text(), '방문자 리뷰') or contains(@href, '/review/visitor')]")

                for elem in visitor_elements:
                    text = elem.text.strip()
                    if text:
                        count = self.extract_number(text)
                        if count is not None and count > 0:
                            data['visitor_reviews'] = count
                            print(f"✓ Visitor reviews: {count:,}")
                            break
            except Exception as e:
                print(f"Could not extract visitor reviews: {e}")

            # Extract blog reviews
            try:
                blog_elements = self.driver.find_elements(By.XPATH,
                    "//*[contains(text(), '블로그리뷰') or contains(text(), '블로그 리뷰') or contains(@href, '/review/ugc')]")

                for elem in blog_elements:
                    text = elem.text.strip()
                    if text:
                        count = self.extract_number(text)
                        if count is not None and count > 0:
                            data['blog_reviews'] = count
                            print(f"✓ Blog reviews: {count:,}")
                            break
            except Exception as e:
                print(f"Could not extract blog reviews: {e}")

            # Extract rating
            try:
                rating_elements = self.driver.find_elements(By.XPATH,
                    "//*[contains(@class, 'rating') or contains(@class, 'score')]//em | //*[contains(@class, 'rating')]")

                for elem in rating_elements:
                    text = elem.text.strip()
                    if text:
                        # Try to parse as float
                        rating_match = re.search(r'(\d+\.?\d*)', text)
                        if rating_match:
                            try:
                                rating = float(rating_match.group(1))
                                if 0 <= rating <= 5:
                                    data['naver_rating'] = rating
                                    print(f"✓ Rating: {rating}")
                                    break
                            except:
                                pass
            except Exception as e:
                print(f"Could not extract rating: {e}")

            # Extract AI Briefing
            try:
                ai_elements = self.driver.find_elements(By.XPATH,
                    "//*[contains(@class, 'ai') or contains(@class, 'AI')]")

                for elem in ai_elements:
                    text = elem.text.strip()
                    if text and len(text) > 20:  # AI briefings are usually longer
                        data['ai_briefing'] = text
                        print(f"✓ AI Briefing found: {text[:50]}...")
                        break
            except Exception as e:
                print(f"Could not extract AI briefing: {e}")

        except Exception as e:
            print(f"⚠️ Error fetching restaurant data: {e}")
            import traceback
            traceback.print_exc()

        return data

    def display_results(self, data: Optional[Dict[str, Any]]) -> None:
        """Display the retrieved restaurant data in a formatted way."""
        if not data:
            print("\n❌ No data found.")
            return

        print("\n" + "="*60)
        print(f"🍴 Restaurant: {data['restaurant_name']}")
        print("="*60)
        print(f"📍 Place ID: {data['place_id']}")
        print(f"🔗 Naver Maps URL: {data['naver_maps_url']}")
        print(f"📱 Mobile Place URL: {data['naver_place_url']}")
        print(f"\n📊 Reviews & Ratings:")
        print(f"   👥 Visitor Reviews: {data['visitor_reviews'] if data['visitor_reviews'] is not None else 'N/A'}")
        print(f"   📝 Blog Reviews: {data['blog_reviews'] if data['blog_reviews'] is not None else 'N/A'}")
        print(f"   ⭐ Naver Rating: {data['naver_rating'] if data['naver_rating'] is not None else 'N/A'}")
        print(f"\n🤖 AI Briefing:")
        print(f"   {data['ai_briefing'] if data['ai_briefing'] else 'Not available'}")
        print("="*60)


def main():
    """Main function to run the scraper"""
    import sys

    # Get restaurant name from command line or use default
    if len(sys.argv) > 1:
        restaurant_name = ' '.join(sys.argv[1:])
    else:
        restaurant_name = "디핀옥수"
        print(f"No restaurant name provided. Using example: {restaurant_name}")
        print("Usage: python naver_restaurant_scraper_selenium.py <restaurant name>")
        print()

    # Create scraper and search
    scraper = NaverRestaurantScraperSelenium()
    data = scraper.search_restaurant(restaurant_name)

    # Display results
    if data:
        scraper.display_results(data)

        # Also output JSON
        print("\n📄 JSON Output:")
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print("❌ Restaurant not found.")


if __name__ == "__main__":
    main()
