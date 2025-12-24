# Install required packages
# !apt-get update > /dev/null 2>&1
# !apt-get install -y wget unzip > /dev/null 2>&1
# !wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# !apt-get install -y ./google-chrome-stable_current_amd64.deb > /dev/null 2>&1
# !pip install webdriver-manager selenium requests beautifulsoup4 pandas -q

# Import libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import re
import urllib.parse

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--lang=ko-KR')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def extract_number(text):
    if not text: return 0
    match = re.search(r'(\d+(?:,\d+)*)', text)
    if match: return int(match.group(1).replace(',', ''))
    return 0

def clean_ai_briefing(text):
    if not text: return ""
    lines = text.split('\n')
    summary_lines = []

    for line in lines:
        line = line.strip()
        if not line: continue
        if line in ['내부', '외부', '음식·음료', '메뉴판', '분위기', '서비스', '특징']: break
        if re.search(r'\d{2}\.\d{2}\.\d{2}', line) or re.search(r'\d{4}년\s*\d{1,2}월', line): break
        if line in ['AI 브리핑', '안내', '새로워진 키워드']: continue
        if '실험 단계' in line or '정확하지 않을 수 있어요' in line: continue
        if '리뷰를 요약하면' in line or '요약하면 다음과 같습니다' in line: continue
        if re.match(r'^\d+$', line): continue

        cleaned = re.sub(r'\[\d+\]', '', line)
        cleaned = re.sub(r'\(\d+\)', '', cleaned)
        cleaned = re.sub(r'^\d+\.\s*', '', cleaned)
        cleaned = re.sub(r'[¹²³⁴⁵⁶⁷⁸⁹⁰]+', '', cleaned)
        cleaned = re.sub(r'\s+\d+\s*$', '', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        if len(cleaned) > 1: summary_lines.append(cleaned)

    return '\n'.join(summary_lines).strip()

def get_place_id_by_search(driver, query):
    print(f"\n🔍 Searching for: {query}")
    encoded_query = urllib.parse.quote(query)
    url = f"https://m.place.naver.com/place/list?query={encoded_query}"
    driver.get(url)
    time.sleep(3)

    try:
        current_url = driver.current_url
        if "/restaurant/" in current_url:
            match = re.search(r'/restaurant/(\d+)', current_url)
            if match:
                print(f"✓ Found direct redirect! Place ID: {match.group(1)}")
                return match.group(1)

        try:
            xpath = "//a[contains(@href, '/restaurant/')]"
            first_link = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath)))
            href = first_link.get_attribute("href")
            match = re.search(r'/restaurant/(\d+)', href)
            if match:
                print(f"✓ Found link in list! Place ID: {match.group(1)}")
                return match.group(1)
        except: pass

        try:
            script_data = driver.find_element(By.ID, "__NEXT_DATA__").get_attribute("innerHTML")
            ids = re.findall(r'"id":"(\d{8,})"', script_data)
            if ids:
                print(f"✓ Found ID in JSON data! Place ID: {ids[0]}")
                return ids[0]
        except: pass

    except Exception as e: print(f"⚠ Search Error: {e}")
    print("❌ Could not find Place ID")
    return None

def extract_review_keywords_robust(driver, debug=True):
    """
    Extracts review keywords with multiple fallback strategies and better debugging.
    """
    keywords = {}
    print("   ...Extracting ALL 'Good Points' (이런 점이 좋았어요)")

    try:
        # 1. Scroll to section - more aggressive
        scrolled = False
        try:
            # Method 1: Find by exact text
            header = driver.find_element(By.XPATH, "//*[contains(text(), '이런 점이 좋았어요')]")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", header)
            time.sleep(2)
            if debug: print("   [DEBUG] Found and scrolled to '이런 점이 좋았어요' header")
            scrolled = True
        except:
            pass

        # Try multiple scroll positions to ensure keywords are visible
        if not scrolled:
            for scroll_pos in [400, 800, 1200, 1600, 2000]:
                driver.execute_script(f"window.scrollTo(0, {scroll_pos});")
                time.sleep(1)
                # Check if we can see the header now
                try:
                    driver.find_element(By.XPATH, "//*[contains(text(), '이런 점이 좋았어요')]")
                    if debug: print(f"   [DEBUG] Found header at scroll position {scroll_pos}")
                    time.sleep(1)
                    scrolled = True
                    break
                except:
                    continue

        if not scrolled and debug:
            print("   [DEBUG] Could not find '이런 점이 좋았어요' header, scrolled through page")

        # 2. Expand the list multiple times
        max_clicks = 20
        successful_clicks = 0
        for i in range(max_clicks):
            try:
                # Try multiple selectors for the expand button
                expand_selectors = [
                    "//button[contains(text(), '펼쳐보기')]",
                    "//a[contains(text(), '펼쳐보기')]",
                    "//button[contains(text(), '더보기')]",
                    "//a[contains(text(), '더보기')]",
                    "//a[contains(@class, 'Tvx37')]",
                    "//*[contains(@class, 'fvwqf')]"
                ]

                btn = None
                for selector in expand_selectors:
                    try:
                        btn = driver.find_element(By.XPATH, selector)
                        if btn.is_displayed():
                            break
                    except:
                        continue

                if btn and btn.is_displayed():
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(1.5)
                    successful_clicks += 1
                    if debug and i % 5 == 0: print(f"   [DEBUG] Clicked expand button {successful_clicks} times")
                else:
                    break
            except:
                break

        if successful_clicks > 0:
            print(f"   ✓ Expanded list {successful_clicks} times")

        # Give extra time for content to fully load
        time.sleep(2)

        # 3. STRATEGY 1: Try to find elements directly with Selenium first
        if debug: print("   [DEBUG] Trying Strategy 1: Direct Selenium search...")
        try:
            # First, try to find specific keyword list items that have both text and numbers
            # Look for LI elements that contain Korean endings and numbers
            keyword_selectors = [
                "//li[contains(., '어요') and contains(., '이 키워드를 선택한 인원')]",
                "//li[contains(., '해요') and contains(., '이 키워드를 선택한 인원')]",
                "//li[contains(@class, 'pui__') and (contains(., '어요') or contains(., '해요'))]",
                "//ul[contains(@class, 'pui__')]//li",
                "//div[contains(@class, 'place_section_content')]//li"
            ]

            for selector in keyword_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    if len(elements) > 5:  # If we found a reasonable number
                        if debug: print(f"   [DEBUG] Found {len(elements)} elements with selector: {selector}")

                        for elem in elements:
                            text = elem.text.strip()
                            if not text or len(text) < 3:
                                continue

                            # Skip navigation items
                            if text in ["업체", "클립", "내부", "외부", "홈", "메뉴", "리뷰"]:
                                continue

                            # Try to parse "keyword + number" pattern
                            lines = text.split('\n')
                            for line in lines:
                                line = line.strip()
                                # Skip aria-label text
                                if '이 키워드를 선택한 인원' in line:
                                    # Extract from aria-label pattern: "keyword 이 키워드를 선택한 인원 number명"
                                    match = re.search(r'(.+?)\s*이 키워드를 선택한 인원\s*(\d+(?:,\d+)*)', line)
                                    if match:
                                        phrase = match.group(1).strip()
                                        count = extract_number(match.group(2))
                                        if count > 0 and 3 < len(phrase) < 60:
                                            if phrase not in keywords:
                                                keywords[phrase] = count
                                                if debug: print(f"   [DEBUG] Found keyword: {phrase} = {count}")
                                    continue

                                # Pattern: "음식이 맛있어요 1,490" or split into parts
                                parts = line.split()
                                if len(parts) >= 2:
                                    # Check if last part is a number
                                    if re.match(r'^[\d,]+$', parts[-1]):
                                        count = extract_number(parts[-1])
                                        phrase = ' '.join(parts[:-1]).strip()

                                        if count > 0 and 3 < len(phrase) < 60:
                                            phrase = phrase.replace('"', '').replace("'", "").strip()
                                            if phrase not in keywords:
                                                keywords[phrase] = count
                                                if debug: print(f"   [DEBUG] Found keyword: {phrase} = {count}")

                        if keywords:
                            break  # Found keywords, exit loop
                except Exception as e:
                    if debug: print(f"   [DEBUG] Selector {selector} failed: {e}")
                    continue
        except Exception as e:
            if debug: print(f"   [DEBUG] Strategy 1 failed: {e}")

        # 4. STRATEGY 2: BeautifulSoup parsing with multiple approaches
        if len(keywords) == 0:
            if debug: print("   [DEBUG] Trying Strategy 2: BeautifulSoup parsing...")
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # Try to find the keyword section container
            keyword_section = None

            # Look for section containing the header
            headers = soup.find_all(string=re.compile(r'이런 점이 좋았어요'))
            if headers and debug:
                print(f"   [DEBUG] Found {len(headers)} headers matching '이런 점이 좋았어요'")

            # Try to find UL containers near the header
            potential_sections = []
            for header in headers:
                parent = header.find_parent()
                for level in range(10):  # Go up 10 levels max
                    if parent:
                        # Find all UL elements in this parent
                        uls = parent.find_all('ul')
                        for ul in uls:
                            if ul not in potential_sections:
                                potential_sections.append(ul)
                        parent = parent.find_parent()

            if debug and potential_sections:
                print(f"   [DEBUG] Found {len(potential_sections)} potential UL sections")

            # Validate each section to find the one with actual keywords
            for ul_section in potential_sections:
                li_elements = ul_section.find_all('li')

                # Quick validation: check if this UL has keyword-like items
                has_numbers = False
                has_korean_endings = False

                sample_text = ' '.join([li.get_text() for li in li_elements[:5]])
                if re.search(r'\d{2,}', sample_text):  # Has numbers with 2+ digits
                    has_numbers = True
                if re.search(r'[어해]요', sample_text):  # Has Korean verb endings
                    has_korean_endings = True

                if has_numbers and has_korean_endings:
                    keyword_section = ul_section
                    if debug:
                        print(f"   [DEBUG] Found valid keyword UL with {len(li_elements)} LI elements")
                    break

            # If we found the section, parse it
            if keyword_section:
                li_elements = keyword_section.find_all('li')

                for li in li_elements:
                    # Get all text parts separately
                    parts = [s.strip() for s in li.stripped_strings if s.strip()]

                    if not parts:
                        continue

                    # Only show debug for items that look promising (have multiple parts)
                    if debug and len(parts) >= 2:
                        print(f"   [DEBUG] LI parts: {parts}")

                    # Filter out label text
                    clean_parts = []
                    for part in parts:
                        if "이 키워드를 선택한 인원" in part:
                            continue
                        if part == "명" and len(part) < 3:
                            continue
                        clean_parts.append(part)

                    if len(clean_parts) >= 2:
                        # Find the number part
                        count = 0
                        phrase = ""

                        # Check each part for a number
                        for i, part in enumerate(clean_parts):
                            if re.match(r'^[\d,]+$', part):
                                count = extract_number(part)
                                # The phrase is usually before the count
                                if i > 0:
                                    phrase = clean_parts[i-1]
                                elif i < len(clean_parts) - 1:
                                    phrase = clean_parts[i+1]
                                break

                        if count > 0 and phrase:
                            phrase = phrase.replace('"', '').replace("'", "").strip()

                            # Filter navigation items
                            ignore_list = ["홈", "메뉴", "리뷰", "사진", "지도", "주변", "예약", "주문",
                                         "방문자 리뷰", "블로그 리뷰", "영수증", "이런 점이 좋았어요",
                                         "업체", "클립", "내부", "외부", "동영상", "방문자", "블로그"]

                            if phrase not in ignore_list and 2 < len(phrase) < 60:
                                keywords[phrase] = count
            else:
                # Fallback: Search all LI elements in page
                if debug: print("   [DEBUG] No keyword section found, searching all LI elements...")
                all_lis = soup.find_all('li')

                for li in all_lis:
                    text = li.get_text(strip=True)

                    # Look for pattern with Korean ending + number
                    if re.search(r'[어해]요', text):  # Common Korean verb endings
                        parts = [s.strip() for s in li.stripped_strings if s.strip()]

                        # Try to extract keyword and count
                        for i, part in enumerate(parts):
                            if re.match(r'^[\d,]+$', part):
                                count = extract_number(part)
                                if count > 10:  # Reasonable threshold
                                    # Find the keyword part (usually before the number)
                                    for j in range(i):
                                        candidate = parts[j]
                                        if re.search(r'[어해]요$', candidate) and len(candidate) > 3:
                                            keywords[candidate] = max(keywords.get(candidate, 0), count)
                                            break

        # 5. STRATEGY 3: Regex on page source
        if len(keywords) == 0:
            if debug: print("   [DEBUG] Trying Strategy 3: Regex on page source...")
            page_source = driver.page_source

            # Pattern: Korean text ending in 어요/해요 followed by number
            pattern = r'([가-힣\s]{3,30}[어해]요)[\s\n<>"]*(\d{1,5}(?:,\d{3})*)'
            matches = re.findall(pattern, page_source)

            if debug and matches: print(f"   [DEBUG] Found {len(matches)} regex matches")

            for phrase, count_str in matches:
                phrase = phrase.strip()
                count = extract_number(count_str)

                if count > 10 and 3 < len(phrase) < 60:  # Reasonable thresholds
                    phrase = re.sub(r'<[^>]+>', '', phrase)  # Remove any HTML
                    phrase = re.sub(r'\s+', ' ', phrase).strip()

                    ignore_list = ["홈", "메뉴", "리뷰", "사진", "지도", "주변"]
                    if phrase not in ignore_list:
                        keywords[phrase] = max(keywords.get(phrase, 0), count)

        if keywords:
            print(f"   ✓ Found {len(keywords)} distinct keyword items")
        else:
            print("   ⚠ Found 0 keywords after all strategies")
            if debug:
                # Save page source for debugging
                with open('/tmp/debug_page_source.html', 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                print("   [DEBUG] Saved page source to /tmp/debug_page_source.html")

    except Exception as e:
        print(f"   ⚠ Keyword extraction error: {e}")
        if debug:
            import traceback
            traceback.print_exc()

    return keywords

def get_full_restaurant_data(search_query, debug=True):
    driver = setup_driver()
    results = {}

    try:
        # 1. Get Place ID
        place_id = get_place_id_by_search(driver, search_query)
        if not place_id: return None

        results['place_id'] = place_id
        results['url'] = f"https://m.place.naver.com/restaurant/{place_id}/home"

        # 2. Go to Home Tab
        print(f"⏳ Loading restaurant details...")
        driver.get(results['url'])
        time.sleep(3)
        driver.execute_script("window.scrollTo(0, 1000);")
        time.sleep(1)

        # --- Name ---
        try:
            name_elem = driver.find_element(By.CSS_SELECTOR, "#_title span.Fc1rA, #_title span.GHAhO, span.Fc1rA")
            results['name'] = name_elem.text.strip()
        except: results['name'] = search_query

        # --- Rating ---
        results['rating'] = None
        try:
            rating_elem = driver.find_element(By.CSS_SELECTOR, "span.PXMot.LXIwF, em.PXMot")
            rating_text = rating_elem.text.strip()
            match = re.search(r'(\d+\.?\d*)', rating_text)
            if match: results['rating'] = float(match.group(1))
        except: pass

        # --- AI Briefing ---
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text
            results['ai_briefing'] = ""
            if 'AI 브리핑' in body_text:
                lines = body_text.split('\n')
                start = -1
                for i, line in enumerate(lines):
                    if 'AI 브리핑' in line: start = i; break
                if start != -1:
                    raw_ai = "\n".join(lines[start:min(start+40, len(lines))])
                    results['ai_briefing'] = clean_ai_briefing(raw_ai)
        except: pass

        # 3. Go to Review Tab
        review_url = f"https://m.place.naver.com/restaurant/{place_id}/review/visitor"
        print(f"⏳ Loading review page...")
        driver.get(review_url)
        time.sleep(4)  # Increased wait time

        # --- Review Counts ---
        results['visitor_reviews'] = 0
        results['blog_reviews'] = 0
        html = driver.page_source

        v_match = re.search(r'방문자 리뷰\s*<[^>]+>\s*(\d+(?:,\d+)*)', html)
        if not v_match: v_match = re.search(r'방문자 리뷰.*?(\d+(?:,\d+)*)', html.replace('\n', ' '))
        if v_match: results['visitor_reviews'] = extract_number(v_match.group(1))

        b_match = re.search(r'블로그 리뷰\s*<[^>]+>\s*(\d+(?:,\d+)*)', html)
        if not b_match: b_match = re.search(r'블로그 리뷰.*?(\d+(?:,\d+)*)', html.replace('\n', ' '))
        if b_match: results['blog_reviews'] = extract_number(b_match.group(1))

        # --- Keyword Stats ---
        results['keyword_stats'] = extract_review_keywords_robust(driver, debug=debug)

        return results

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        driver.quit()

# ================================
# 🏁 RUN THE SCRIPT
# ================================

if __name__ == "__main__":
    input_name = "옥수동화덕피자"

    print(f"🎬 Starting crawler for: {input_name}")
    data = get_full_restaurant_data(input_name, debug=True)

    if data:
        print("\n" + "="*60)
        print(f"🥗 RESTAURANT: {data.get('name')}")
        print("="*60)
        print(f"🔗 Place ID: {data['place_id']}")
        print(f"🌐 URL: {data['url']}")
        print(f"⭐ Rating: {data['rating'] if data['rating'] else 'N/A'}")
        print(f"👥 Visitor Reviews: {data['visitor_reviews']:,}")
        print(f"📝 Blog Reviews: {data['blog_reviews']:,}")

        print("\n👍 Review Keywords (이런 점이 좋았어요):")
        if data['keyword_stats']:
            sorted_keywords = sorted(data['keyword_stats'].items(), key=lambda item: item[1], reverse=True)
            for k, v in sorted_keywords:
                print(f'   "{k}": {v:,}')
        else:
            print("   (No keyword stats found)")

        print("\n🤖 AI Briefing:")
        if data['ai_briefing']:
            print("-" * 40)
            print(data['ai_briefing'])
            print("-" * 40)
        else:
            print("   (Not available)")
        print("="*60)
