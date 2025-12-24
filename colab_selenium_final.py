# ============================================================================
# NAVER RESTAURANT SCRAPER - FINAL VERSION FOR GOOGLE COLAB
# Follows exact requirement flow:
# 1. Get Naver Place URL from restaurant name
# 2. Extract Place ID
# 3. Get visitor reviews and blog reviews
# 4. Get Naver rating (optional)
# 5. Get AI Briefing (check Naver Place first, then Maps if not found)
# ============================================================================

# Step 1: Install Chrome and ChromeDriver
print("📦 Installing Chrome and ChromeDriver...")
!apt-get update -qq
!apt-get install -y wget unzip -qq
!wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
!apt-get install -y ./google-chrome-stable_current_amd64.deb -qq

# Get Chrome version
import re
import subprocess
chrome_version = subprocess.check_output(['google-chrome', '--version']).decode('utf-8')
version_match = re.search(r'(\d+\.\d+\.\d+)', chrome_version)
if version_match:
    version = version_match.group(1)
    print(f"✓ Chrome version: {version}")

# Step 2: Install Python packages
print("\n📦 Installing Python packages...")
!pip install -q webdriver-manager selenium

print("✓ All dependencies installed!\n")

# Step 3: Import libraries
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


# Step 4: Define the Scraper Class
class NaverRestaurantScraper:
    """
    Selenium-based scraper for Naver Maps/Place restaurant data

    Flow:
    1. Search restaurant name → Get Naver Place URL
    2. Extract Place ID from URL
    3. Fetch visitor reviews and blog reviews using Place ID
    4. Fetch Naver rating (optional)
    5. Fetch AI Briefing (Naver Place first, then Naver Maps if not found)
    """

    def __init__(self):
        self.driver = None

    def setup_driver(self):
        """Set up Chrome driver with options suitable for Colab"""
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
        Main function: Search for a restaurant and retrieve all data

        Args:
            restaurant_name: Name of the restaurant (e.g., "디핀옥수", "Namaste Wangsimni Branch")

        Returns:
            Dictionary containing all restaurant data
        """
        print(f"🔍 Searching for: {restaurant_name}")
        print("="*60)

        # Set up driver
        if not self.driver:
            print("⚙️  Setting up Chrome WebDriver...")
            self.driver = self.setup_driver()

        try:
            # STEP 1: Retrieve Naver Place URL and extract Place ID
            print("\n📍 STEP 1: Getting Naver Place URL and Place ID...")
            place_id, naver_place_url = self._get_place_url_and_id(restaurant_name)

            if not place_id:
                print(f"❌ Could not find restaurant '{restaurant_name}'")
                return None

            print(f"✓ Place ID: {place_id}")
            print(f"✓ Naver Place URL: {naver_place_url}")

            # STEP 2: Fetch visitor reviews and blog reviews
            print("\n📊 STEP 2: Fetching review counts...")
            visitor_reviews, blog_reviews = self._get_review_counts(place_id, naver_place_url)

            # STEP 3: Fetch Naver rating
            print("\n⭐ STEP 3: Fetching Naver rating...")
            naver_rating = self._get_naver_rating(place_id, naver_place_url)

            # STEP 4: Fetch AI Briefing (Naver Place first, then Maps)
            print("\n🤖 STEP 4: Fetching AI Briefing...")
            ai_briefing = self._get_ai_briefing(place_id, naver_place_url)

            # Compile all data
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
        """
        STEP 1: Search for restaurant and get Naver Place URL + Place ID

        Returns:
            tuple: (place_id, naver_place_url)
        """
        try:
            # Navigate to Naver Maps search
            search_url = f"https://map.naver.com/v5/search/{quote(restaurant_name)}"
            self.driver.get(search_url)
            time.sleep(3)

            # Method 1: Check if redirected directly to place page
            current_url = self.driver.current_url
            place_match = re.search(r'/place/(\d+)', current_url)
            if place_match:
                place_id = place_match.group(1)
                naver_place_url = f"https://m.place.naver.com/restaurant/{place_id}/home"
                return place_id, naver_place_url

            # Method 2: Find place links in search results
            try:
                wait = WebDriverWait(self.driver, 10)
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "a")))
                time.sleep(2)

                links = self.driver.find_elements(By.TAG_NAME, "a")
                for link in links:
                    href = link.get_attribute("href")
                    if href and '/place/' in href:
                        match = re.search(r'/place/(\d+)', href)
                        if match:
                            place_id = match.group(1)
                            naver_place_url = f"https://m.place.naver.com/restaurant/{place_id}/home"
                            return place_id, naver_place_url
            except:
                pass

            # Method 3: Search page source
            page_source = self.driver.page_source
            patterns = [
                r'"id"\s*:\s*"(\d+)"',
                r'"placeId"\s*:\s*"(\d+)"',
                r'/place/(\d+)',
            ]

            for pattern in patterns:
                matches = re.findall(pattern, page_source)
                for match in matches:
                    if match.isdigit() and 5 <= len(match) <= 20:
                        place_id = match
                        naver_place_url = f"https://m.place.naver.com/restaurant/{place_id}/home"
                        return place_id, naver_place_url

            return None, None

        except Exception as e:
            print(f"⚠️ Error getting Place URL: {e}")
            return None, None

    def _get_review_counts(self, place_id: str, naver_place_url: str) -> tuple:
        """
        STEP 2: Fetch visitor reviews and blog reviews using Place ID

        Returns:
            tuple: (visitor_reviews, blog_reviews)
        """
        visitor_reviews = None
        blog_reviews = None

        try:
            # Navigate to Naver Place page
            self.driver.get(naver_place_url)
            time.sleep(4)

            # Extract visitor reviews
            try:
                elements = self.driver.find_elements(By.XPATH,
                    "//*[contains(text(), '방문자리뷰') or contains(text(), '방문자 리뷰')]")
                for elem in elements:
                    count = self.extract_number(elem.text)
                    if count is not None:
                        visitor_reviews = count
                        print(f"  ✓ Visitor reviews: {count:,}")
                        break
            except Exception as e:
                print(f"  ⚠️ Could not extract visitor reviews: {e}")

            # Extract blog reviews
            try:
                elements = self.driver.find_elements(By.XPATH,
                    "//*[contains(text(), '블로그리뷰') or contains(text(), '블로그 리뷰')]")
                for elem in elements:
                    count = self.extract_number(elem.text)
                    if count is not None:
                        blog_reviews = count
                        print(f"  ✓ Blog reviews: {count:,}")
                        break
            except Exception as e:
                print(f"  ⚠️ Could not extract blog reviews: {e}")

        except Exception as e:
            print(f"  ⚠️ Error fetching review counts: {e}")

        if visitor_reviews is None:
            print(f"  ⚠️ Visitor reviews: Not found")
        if blog_reviews is None:
            print(f"  ⚠️ Blog reviews: Not found")

        return visitor_reviews, blog_reviews

    def _get_naver_rating(self, place_id: str, naver_place_url: str) -> Optional[float]:
        """
        STEP 3: Fetch Naver rating (optional - may not be available)

        Returns:
            float: Naver rating or None if not available
        """
        try:
            # Page should already be loaded from previous step
            # Try to find rating
            elements = self.driver.find_elements(By.XPATH,
                "//*[contains(@class, 'place_section_scorearea')]//em | //*[contains(@class, 'score')]//em")

            for elem in elements:
                rating_match = re.search(r'(\d+\.?\d*)', elem.text)
                if rating_match:
                    rating = float(rating_match.group(1))
                    if 0 <= rating <= 5:
                        print(f"  ✓ Naver rating: {rating}")
                        return rating

            print(f"  ℹ️  Naver rating: Not available (omitted)")
            return None

        except Exception as e:
            print(f"  ℹ️  Naver rating: Not available (omitted)")
            return None

    def _get_ai_briefing(self, place_id: str, naver_place_url: str) -> Optional[str]:
        """
        STEP 4: Fetch AI Briefing
        Priority:
        1. Check Naver Place first
        2. If not found, check Naver Maps
        3. Return if found

        Returns:
            str: AI Briefing content or None if not available
        """
        # Priority 1: Check Naver Place (already on this page)
        print(f"  🔍 Checking Naver Place for AI Briefing...")
        try:
            # Try multiple selectors for AI briefing on Naver Place
            ai_selectors = [
                "//*[contains(@class, 'LDgIH')]",  # AI summary class
                "//*[contains(@class, 'ai')]//p",
                "//*[contains(@class, 'AI')]//p",
                "//*[contains(text(), 'AI') and contains(text(), '요약')]//following-sibling::*",
            ]

            for selector in ai_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        if text and len(text) > 10:  # AI briefings are usually longer than 10 chars
                            print(f"  ✓ AI Briefing found on Naver Place!")
                            print(f"    Preview: {text[:50]}...")
                            return text
                except:
                    continue

            print(f"  ℹ️  AI Briefing not found on Naver Place")

        except Exception as e:
            print(f"  ⚠️ Error checking Naver Place: {e}")

        # Priority 2: Check Naver Maps if not found on Naver Place
        print(f"  🔍 Checking Naver Maps for AI Briefing...")
        try:
            maps_url = f"https://map.naver.com/v5/entry/place/{place_id}"
            self.driver.get(maps_url)
            time.sleep(4)

            # Try to find AI briefing on Maps
            ai_selectors = [
                "//*[contains(@class, 'ai')]",
                "//*[contains(@class, 'AI')]",
                "//*[contains(text(), 'AI')]//following-sibling::*",
            ]

            for selector in ai_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        if text and len(text) > 10:
                            print(f"  ✓ AI Briefing found on Naver Maps!")
                            print(f"    Preview: {text[:50]}...")
                            return text
                except:
                    continue

            print(f"  ℹ️  AI Briefing not found on Naver Maps")

        except Exception as e:
            print(f"  ⚠️ Error checking Naver Maps: {e}")

        print(f"  ℹ️  AI Briefing: Not available")
        return None

    def display_results_colab(self, data: Optional[Dict[str, Any]]) -> None:
        """Display results with beautiful Colab formatting"""
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
                <li><strong>⭐ Naver Rating:</strong> {data['naver_rating'] if data['naver_rating'] is not None else 'Not available (omitted)'}</li>
            </ul>

            <hr style="border: 0.5px solid #ddd;">

            <h3>🤖 AI Briefing</h3>
            <p style="background-color: white; padding: 15px; border-radius: 5px; border-left: 4px solid #4CAF50;">
                {data['ai_briefing'] if data['ai_briefing'] else '<em style="color: #999;">Not available</em>'}
            </p>
        </div>
        """

        display(HTML(html))

        # Display as DataFrame
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
# USAGE - Change the restaurant name below and run!
# ============================================================================

print("\n" + "="*60)
print("🚀 Naver Restaurant Scraper - Final Version")
print("="*60)
print("\nExecution Flow:")
print("1. Get Naver Place URL from restaurant name")
print("2. Extract Place ID")
print("3. Get visitor reviews and blog reviews")
print("4. Get Naver rating (optional)")
print("5. Get AI Briefing (Naver Place → Naver Maps)")
print("="*60 + "\n")

# Enter your restaurant name here
restaurant_name = "디핀옥수"  # ← Change this to your restaurant!

# Create scraper and search
scraper = NaverRestaurantScraper()
data = scraper.search_restaurant(restaurant_name)

# Display results
if data:
    scraper.display_results_colab(data)

    # Show JSON output
    print("\n" + "="*60)
    print("📄 JSON Output:")
    print("="*60)
    print(json.dumps(data, ensure_ascii=False, indent=2))
else:
    print("\n❌ Restaurant not found. Please try:")
    print("  1. Check the restaurant name spelling")
    print("  2. Try using the Korean name")
    print("  3. Include location details (e.g., '강남점', 'Gangnam Branch')")
