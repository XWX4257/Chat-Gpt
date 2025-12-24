# ============================================================================
# NAVER RESTAURANT SCRAPER - FIXED VERSION FOR GOOGLE COLAB
# Enhanced with better iframe handling and robust search
# ============================================================================

# Step 1: Install Chrome and ChromeDriver
print("📦 Installing Chrome and ChromeDriver...")
!apt-get update -qq
!apt-get install -y wget unzip -qq
!wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
!apt-get install -y ./google-chrome-stable_current_amd64.deb -qq

import re
import subprocess
chrome_version = subprocess.check_output(['google-chrome', '--version']).decode('utf-8')
version_match = re.search(r'(\d+\.\d+\.\d+)', chrome_version)
if version_match:
    version = version_match.group(1)
    print(f"✓ Chrome version: {version}")

print("\n📦 Installing Python packages...")
!pip install -q webdriver-manager selenium

print("✓ All dependencies installed!\n")

# Import libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from IPython.display import display, HTML, JSON
import pandas as pd
import time
import json
from typing import Optional, Dict, Any
from urllib.parse import quote


class NaverRestaurantScraper:
    """Enhanced Selenium-based scraper with iframe handling"""

    def __init__(self):
        self.driver = None

    def setup_driver(self):
        """Set up Chrome driver"""
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
        """Extract number from text"""
        if not text:
            return None
        match = re.search(r'(\d+(?:,\d+)*)', text)
        if match:
            return int(match.group(1).replace(',', ''))
        return None

    def search_restaurant(self, restaurant_name: str) -> Optional[Dict[str, Any]]:
        """Main search function"""
        print(f"🔍 Searching for: {restaurant_name}")
        print("="*60)

        if not self.driver:
            print("⚙️  Setting up Chrome WebDriver...")
            self.driver = self.setup_driver()

        try:
            # STEP 1: Get Place ID
            print("\n📍 STEP 1: Getting Naver Place URL and Place ID...")
            place_id, naver_place_url = self._get_place_url_and_id(restaurant_name)

            if not place_id:
                print(f"❌ Could not find restaurant '{restaurant_name}'")
                return None

            print(f"✓ Place ID: {place_id}")
            print(f"✓ Naver Place URL: {naver_place_url}")

            # STEP 2: Fetch reviews
            print("\n📊 STEP 2: Fetching review counts...")
            visitor_reviews, blog_reviews = self._get_review_counts(place_id, naver_place_url)

            # STEP 3: Fetch rating
            print("\n⭐ STEP 3: Fetching Naver rating...")
            naver_rating = self._get_naver_rating(place_id, naver_place_url)

            # STEP 4: Fetch AI Briefing
            print("\n🤖 STEP 4: Fetching AI Briefing...")
            ai_briefing = self._get_ai_briefing(place_id, naver_place_url)

            data = {
                'restaurant_name': restaurant_name,
                'place_id': place_id,
                'naver_place_url': naver_place_url,
                'naver_maps_url': f"https://map.naver.com/v5/entry/place/{place_id}",
                'visitor_reviews': visitor_reviews,
                'blog_reviews': blog_reviews,
                'naver_rating': naver_rating,
                'ai_briefing': ai_briefing
            }

            print("\n" + "="*60)
            print("✅ Data retrieval complete!")
            print("="*60)

            return data

        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None

    def _get_place_url_and_id(self, restaurant_name: str) -> tuple:
        """Enhanced place ID search with iframe handling"""
        try:
            # Method 1: Try Naver Maps search
            print(f"  🔍 Searching Naver Maps...")
            search_url = f"https://map.naver.com/v5/search/{quote(restaurant_name)}"
            self.driver.get(search_url)
            time.sleep(5)  # Longer wait for page load

            # Check URL for redirect
            current_url = self.driver.current_url
            print(f"  📍 Current URL: {current_url[:80]}...")

            place_match = re.search(r'/place/(\d+)', current_url)
            if place_match:
                place_id = place_match.group(1)
                print(f"  ✓ Found in URL redirect")
                return place_id, f"https://m.place.naver.com/restaurant/{place_id}/home"

            # Check for iframes
            print(f"  🔍 Checking for iframes...")
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            print(f"  📍 Found {len(iframes)} iframes")

            # Try switching to searchIframe
            for iframe in iframes:
                try:
                    iframe_id = iframe.get_attribute('id')
                    if iframe_id and 'search' in iframe_id.lower():
                        print(f"  🔍 Switching to iframe: {iframe_id}")
                        self.driver.switch_to.frame(iframe)
                        time.sleep(2)

                        # Look for place links in iframe
                        links = self.driver.find_elements(By.TAG_NAME, "a")
                        for link in links:
                            href = link.get_attribute("href")
                            if href and '/place/' in href:
                                match = re.search(r'/place/(\d+)', href)
                                if match:
                                    place_id = match.group(1)
                                    print(f"  ✓ Found in iframe")
                                    self.driver.switch_to.default_content()
                                    return place_id, f"https://m.place.naver.com/restaurant/{place_id}/home"

                        self.driver.switch_to.default_content()
                except:
                    self.driver.switch_to.default_content()
                    continue

            # Method 2: Search page source
            print(f"  🔍 Searching page source...")
            page_source = self.driver.page_source

            patterns = [
                r'/place/(\d+)',
                r'"id"\s*:\s*"(\d+)"',
                r'"placeId"\s*:\s*"(\d+)"',
                r'data-id="(\d+)"',
            ]

            for pattern in patterns:
                matches = re.findall(pattern, page_source)
                for match in matches:
                    if match.isdigit() and 6 <= len(match) <= 20:
                        place_id = match
                        print(f"  ✓ Found in page source: {place_id}")
                        return place_id, f"https://m.place.naver.com/restaurant/{place_id}/home"

            # Method 3: Try direct mobile search
            print(f"  🔍 Trying mobile Naver Place search...")
            mobile_search_url = f"https://m.place.naver.com/search?query={quote(restaurant_name)}"
            self.driver.get(mobile_search_url)
            time.sleep(5)

            # Check for redirect or links
            current_url = self.driver.current_url
            place_match = re.search(r'/restaurant/(\d+)', current_url)
            if place_match:
                place_id = place_match.group(1)
                print(f"  ✓ Found via mobile search")
                return place_id, f"https://m.place.naver.com/restaurant/{place_id}/home"

            # Look for restaurant links
            links = self.driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                href = link.get_attribute("href")
                if href and '/restaurant/' in href:
                    match = re.search(r'/restaurant/(\d+)', href)
                    if match:
                        place_id = match.group(1)
                        print(f"  ✓ Found in mobile search results")
                        return place_id, f"https://m.place.naver.com/restaurant/{place_id}/home"

            print(f"  ❌ Could not find place ID")
            return None, None

        except Exception as e:
            print(f"  ⚠️ Error: {e}")
            import traceback
            traceback.print_exc()
            return None, None

    def _get_review_counts(self, place_id: str, naver_place_url: str) -> tuple:
        """Fetch review counts"""
        visitor_reviews = None
        blog_reviews = None

        try:
            self.driver.get(naver_place_url)
            time.sleep(5)

            # Extract visitor reviews
            try:
                elements = self.driver.find_elements(By.XPATH,
                    "//*[contains(text(), '방문자리뷰') or contains(text(), '방문자 리뷰') or contains(text(), 'visitor')]")
                for elem in elements:
                    text = elem.text
                    count = self.extract_number(text)
                    if count is not None:
                        visitor_reviews = count
                        print(f"  ✓ Visitor reviews: {count:,}")
                        break
            except:
                pass

            # Extract blog reviews
            try:
                elements = self.driver.find_elements(By.XPATH,
                    "//*[contains(text(), '블로그리뷰') or contains(text(), '블로그 리뷰') or contains(text(), 'blog')]")
                for elem in elements:
                    text = elem.text
                    count = self.extract_number(text)
                    if count is not None:
                        blog_reviews = count
                        print(f"  ✓ Blog reviews: {count:,}")
                        break
            except:
                pass

            # Try alternative: look for review tabs
            try:
                review_tabs = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'review')]")
                for tab in review_tabs:
                    text = tab.text
                    if '방문자' in text and visitor_reviews is None:
                        count = self.extract_number(text)
                        if count:
                            visitor_reviews = count
                            print(f"  ✓ Visitor reviews (from tab): {count:,}")
                    elif '블로그' in text and blog_reviews is None:
                        count = self.extract_number(text)
                        if count:
                            blog_reviews = count
                            print(f"  ✓ Blog reviews (from tab): {count:,}")
            except:
                pass

        except Exception as e:
            print(f"  ⚠️ Error: {e}")

        if visitor_reviews is None:
            print(f"  ⚠️ Visitor reviews: Not found")
        if blog_reviews is None:
            print(f"  ⚠️ Blog reviews: Not found")

        return visitor_reviews, blog_reviews

    def _get_naver_rating(self, place_id: str, naver_place_url: str) -> Optional[float]:
        """Fetch Naver rating"""
        try:
            # Try multiple selectors
            selectors = [
                "//em[contains(@class, 'score')]",
                "//*[contains(@class, 'rating')]//em",
                "//span[contains(@class, 'score')]",
                "//*[@class='place_section_scorearea']//em"
            ]

            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        rating_match = re.search(r'(\d+\.?\d*)', text)
                        if rating_match:
                            rating = float(rating_match.group(1))
                            if 0 <= rating <= 5:
                                print(f"  ✓ Naver rating: {rating}")
                                return rating
                except:
                    continue

            print(f"  ℹ️  Naver rating: Not available (omitted)")
            return None

        except:
            print(f"  ℹ️  Naver rating: Not available (omitted)")
            return None

    def _get_ai_briefing(self, place_id: str, naver_place_url: str) -> Optional[str]:
        """Fetch AI Briefing with priority: Naver Place → Naver Maps"""
        # Priority 1: Naver Place
        print(f"  🔍 Checking Naver Place for AI Briefing...")
        try:
            selectors = [
                "//*[contains(@class, 'LDgIH')]",
                "//*[contains(@class, 'ai')]",
                "//*[contains(@class, 'AI')]",
                "//*[contains(text(), 'AI')]//parent::*//following-sibling::*"
            ]

            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        if text and len(text) > 20 and 'AI' not in text:
                            print(f"  ✓ AI Briefing found on Naver Place!")
                            print(f"    Preview: {text[:50]}...")
                            return text
                except:
                    continue
        except:
            pass

        print(f"  ℹ️  AI Briefing not found on Naver Place")

        # Priority 2: Naver Maps
        print(f"  🔍 Checking Naver Maps for AI Briefing...")
        try:
            maps_url = f"https://map.naver.com/v5/entry/place/{place_id}"
            self.driver.get(maps_url)
            time.sleep(5)

            # Check for iframe
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                try:
                    iframe_id = iframe.get_attribute('id')
                    if iframe_id and 'entry' in iframe_id.lower():
                        self.driver.switch_to.frame(iframe)
                        time.sleep(2)

                        selectors = [
                            "//*[contains(@class, 'ai')]",
                            "//*[contains(@class, 'AI')]"
                        ]

                        for selector in selectors:
                            try:
                                elements = self.driver.find_elements(By.XPATH, selector)
                                for elem in elements:
                                    text = elem.text.strip()
                                    if text and len(text) > 20:
                                        print(f"  ✓ AI Briefing found on Naver Maps!")
                                        print(f"    Preview: {text[:50]}...")
                                        self.driver.switch_to.default_content()
                                        return text
                            except:
                                continue

                        self.driver.switch_to.default_content()
                except:
                    self.driver.switch_to.default_content()
                    continue
        except:
            pass

        print(f"  ℹ️  AI Briefing: Not available")
        return None

    def display_results_colab(self, data: Optional[Dict[str, Any]]) -> None:
        """Display results"""
        if not data:
            display(HTML('<h3 style="color: red;">❌ No data found.</h3>'))
            return

        html = f"""
        <div style="border: 2px solid #4CAF50; border-radius: 10px; padding: 20px; background-color: #f9f9f9;">
            <h2 style="color: #4CAF50; margin-top: 0;">🍴 {data['restaurant_name']}</h2>
            <hr style="border: 1px solid #4CAF50;">

            <p><strong>📍 Place ID:</strong> <code>{data['place_id']}</code></p>
            <p><strong>🔗 Naver Place URL:</strong> <a href="{data['naver_place_url']}" target="_blank">Open Naver Place</a></p>
            <p><strong>🗺️ Naver Maps URL:</strong> <a href="{data['naver_maps_url']}" target="_blank">Open Naver Maps</a></p>

            <hr style="border: 0.5px solid #ddd;">

            <h3>📊 Reviews & Ratings</h3>
            <ul>
                <li><strong>👥 Visitor Reviews:</strong> {f"{data['visitor_reviews']:,}" if data['visitor_reviews'] is not None else 'N/A'}</li>
                <li><strong>📝 Blog Reviews:</strong> {f"{data['blog_reviews']:,}" if data['blog_reviews'] is not None else 'N/A'}</li>
                <li><strong>⭐ Naver Rating:</strong> {data['naver_rating'] if data['naver_rating'] is not None else 'Not available'}</li>
            </ul>

            <hr style="border: 0.5px solid #ddd;">

            <h3>🤖 AI Briefing</h3>
            <p style="background-color: white; padding: 15px; border-radius: 5px; border-left: 4px solid #4CAF50;">
                {data['ai_briefing'] if data['ai_briefing'] else '<em style="color: #999;">Not available</em>'}
            </p>
        </div>
        """

        display(HTML(html))

        print("\n📋 Data Table:")
        df = pd.DataFrame([{
            'Restaurant': data['restaurant_name'],
            'Place ID': data['place_id'],
            'Visitor Reviews': data['visitor_reviews'],
            'Blog Reviews': data['blog_reviews'],
            'Rating': data['naver_rating'] if data['naver_rating'] is not None else 'N/A'
        }])
        display(df)


# ============================================================================
# USAGE
# ============================================================================

print("\n" + "="*60)
print("🚀 Naver Restaurant Scraper - Fixed Version")
print("="*60)
print("\nEnhanced with:")
print("✓ Iframe handling for Naver Maps")
print("✓ Mobile Naver Place fallback")
print("✓ Multiple search strategies")
print("✓ Better debugging output")
print("="*60 + "\n")

# Enter your restaurant name here
restaurant_name = "디핀옥수"  # ← Change this!

# Create scraper and search
scraper = NaverRestaurantScraper()
data = scraper.search_restaurant(restaurant_name)

# Display results
if data:
    scraper.display_results_colab(data)

    print("\n" + "="*60)
    print("📄 JSON Output:")
    print("="*60)
    print(json.dumps(data, ensure_ascii=False, indent=2))
else:
    print("\n❌ Restaurant not found.")
    print("💡 Tips:")
    print("  1. Try the full restaurant name")
    print("  2. Include location (e.g., '옥수동', '왕십리점')")
    print("  3. Try variations of the name")
