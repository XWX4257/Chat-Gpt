# ============================================================================
# NAVER RESTAURANT SCRAPER - SELENIUM VERSION FOR GOOGLE COLAB
# This version uses Selenium with Chrome to handle JavaScript content
# Copy and paste this ENTIRE code into Google Colab and run it!
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
    major_version = version.split('.')[0]
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
    """Selenium-based scraper for Naver Maps/Place restaurant data"""

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
        """Extract number from text, handling Korean formatting"""
        if not text:
            return None
        match = re.search(r'(\d+(?:,\d+)*)', text)
        if match:
            return int(match.group(1).replace(',', ''))
        return None

    def search_restaurant(self, restaurant_name: str) -> Optional[Dict[str, Any]]:
        """Search for a restaurant and retrieve all data"""
        print(f"🔍 Searching for: {restaurant_name}")

        # Set up driver
        if not self.driver:
            print("Setting up Chrome WebDriver...")
            self.driver = self.setup_driver()

        try:
            # Step 1: Search and get place ID
            place_id = self._search_for_place_id(restaurant_name)
            if not place_id:
                print(f"❌ Could not find place ID for '{restaurant_name}'")
                return None

            print(f"✓ Found Place ID: {place_id}")

            # Step 2: Get restaurant data
            restaurant_data = self._get_restaurant_data(place_id, restaurant_name)
            return restaurant_data

        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None

    def _search_for_place_id(self, restaurant_name: str) -> Optional[str]:
        """Search Naver Maps and extract place ID"""
        try:
            # Navigate to search
            search_url = f"https://map.naver.com/v5/search/{quote(restaurant_name)}"
            print(f"Accessing: {search_url}")
            self.driver.get(search_url)
            time.sleep(3)

            # Method 1: Check if redirected to place page
            current_url = self.driver.current_url
            place_match = re.search(r'/place/(\d+)', current_url)
            if place_match:
                return place_match.group(1)

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
                            return match.group(1)
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
                        return match

            return None

        except Exception as e:
            print(f"⚠️ Error: {e}")
            return None

    def _get_restaurant_data(self, place_id: str, restaurant_name: str) -> Dict[str, Any]:
        """Retrieve detailed restaurant data"""
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

        # Access mobile Naver Place page
        mobile_url = f"https://m.place.naver.com/restaurant/{place_id}/home"
        print(f"Fetching data from: {mobile_url}")

        try:
            self.driver.get(mobile_url)
            time.sleep(4)

            # Extract visitor reviews
            try:
                elements = self.driver.find_elements(By.XPATH,
                    "//*[contains(text(), '방문자리뷰') or contains(text(), '방문자 리뷰')]")
                for elem in elements:
                    count = self.extract_number(elem.text)
                    if count:
                        data['visitor_reviews'] = count
                        print(f"✓ Visitor reviews: {count:,}")
                        break
            except:
                pass

            # Extract blog reviews
            try:
                elements = self.driver.find_elements(By.XPATH,
                    "//*[contains(text(), '블로그리뷰') or contains(text(), '블로그 리뷰')]")
                for elem in elements:
                    count = self.extract_number(elem.text)
                    if count:
                        data['blog_reviews'] = count
                        print(f"✓ Blog reviews: {count:,}")
                        break
            except:
                pass

            # Extract rating
            try:
                elements = self.driver.find_elements(By.XPATH,
                    "//*[contains(@class, 'place_section_scorearea')]//em | //*[contains(@class, 'score')]//em")
                for elem in elements:
                    rating_match = re.search(r'(\d+\.?\d*)', elem.text)
                    if rating_match:
                        rating = float(rating_match.group(1))
                        if 0 <= rating <= 5:
                            data['naver_rating'] = rating
                            print(f"✓ Rating: {rating}")
                            break
            except:
                pass

            # Extract AI Briefing
            try:
                elements = self.driver.find_elements(By.XPATH,
                    "//*[contains(@class, 'LDgIH')]")  # AI summary class
                for elem in elements:
                    text = elem.text.strip()
                    if text and len(text) > 10:
                        data['ai_briefing'] = text
                        print(f"✓ AI Briefing: {text[:50]}...")
                        break
            except:
                pass

        except Exception as e:
            print(f"⚠️ Error fetching data: {e}")

        return data

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
            <p><strong>🔗 Naver Maps:</strong> <a href="{data['naver_maps_url']}" target="_blank">Open in Naver Maps</a></p>
            <p><strong>📱 Mobile Place:</strong> <a href="{data['naver_place_url']}" target="_blank">Open Mobile Page</a></p>

            <hr style="border: 0.5px solid #ddd;">

            <h3>📊 Reviews & Ratings</h3>
            <ul>
                <li><strong>👥 Visitor Reviews:</strong> {data['visitor_reviews'] if data['visitor_reviews'] else 'N/A'}</li>
                <li><strong>📝 Blog Reviews:</strong> {data['blog_reviews'] if data['blog_reviews'] else 'N/A'}</li>
                <li><strong>⭐ Naver Rating:</strong> {data['naver_rating'] if data['naver_rating'] else 'N/A'}</li>
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
            'Rating': data['naver_rating']
        }])
        display(df)


# ============================================================================
# USAGE - Change the restaurant name below and run!
# ============================================================================

print("\n" + "="*60)
print("🚀 Naver Restaurant Scraper - Selenium Version")
print("="*60 + "\n")

# Enter your restaurant name here
restaurant_name = "디핀옥수"  # ← Change this to your restaurant!

# Create scraper and search
scraper = NaverRestaurantScraper()
data = scraper.search_restaurant(restaurant_name)

# Display results
if data:
    print("\n" + "="*60)
    print("✅ SUCCESS! Restaurant data retrieved")
    print("="*60 + "\n")

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
