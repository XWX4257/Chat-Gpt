"""
Naver Place Review Crawler
Crawls review counts from Naver Place restaurant pages
Compatible with Google Colab
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import re


def setup_driver():
    """Set up Chrome driver with options suitable for Colab"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36')

    driver = webdriver.Chrome(options=chrome_options)
    return driver


def extract_number(text):
    """Extract number from Korean text, handling commas"""
    if not text:
        return 0
    # Find numbers with or without commas
    match = re.search(r'(\d+(?:,\d+)*)', text)
    if match:
        return int(match.group(1).replace(',', ''))
    return 0


def crawl_naver_place_reviews(url):
    """
    Crawl review counts from a Naver Place restaurant page

    Args:
        url: URL of the Naver Place restaurant review page

    Returns:
        dict: Dictionary containing review counts
    """
    driver = None
    try:
        driver = setup_driver()
        print(f"Accessing URL: {url}")
        driver.get(url)

        # Wait for page to load completely
        time.sleep(5)

        results = {
            'url': url,
            'total_reviews': 0,
            'visitor_reviews': 0,
            'blog_reviews': 0
        }

        wait = WebDriverWait(driver, 15)

        print("\n=== Starting Review Count Extraction ===\n")

        # Strategy 1: Try to find review tabs with counts
        try:
            # Look for tab navigation elements
            tab_selectors = [
                "//a[contains(@href, '/review/visitor')]",
                "//button[contains(@class, 'tab')]",
                "//div[contains(@class, 'tab')]//a",
                "//*[contains(@class, 'review_tab')]",
                "//*[contains(@class, 'place_section_nav')]//a"
            ]

            for selector in tab_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        if text and ('방문자' in text or 'visitor' in text.lower()):
                            count = extract_number(text)
                            if count > 0:
                                results['visitor_reviews'] = count
                                print(f"✓ Found visitor reviews: {count:,} (from: '{text}')")
                                break
                    if results['visitor_reviews'] > 0:
                        break
                except:
                    continue
        except Exception as e:
            print(f"Strategy 1 failed: {e}")

        # Strategy 2: Try to find blog review count
        try:
            blog_selectors = [
                "//a[contains(@href, '/review/ugc')]",
                "//a[contains(@href, 'blog')]",
                "//*[contains(text(), '블로그')]",
                "//*[contains(@class, 'blog')]"
            ]

            for selector in blog_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        if text and '블로그' in text:
                            count = extract_number(text)
                            if count > 0:
                                results['blog_reviews'] = count
                                print(f"✓ Found blog reviews: {count:,} (from: '{text}')")
                                break
                    if results['blog_reviews'] > 0:
                        break
                except:
                    continue
        except Exception as e:
            print(f"Strategy 2 failed: {e}")

        # Strategy 3: Look for review section headers
        try:
            header_selectors = [
                "//*[contains(@class, 'place_section_header')]",
                "//*[contains(@class, 'review')]//h2",
                "//*[contains(@class, 'review')]//h3",
                "//h2 | //h3"
            ]

            for selector in header_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        if '리뷰' in text:
                            count = extract_number(text)
                            if count > results['total_reviews']:
                                print(f"✓ Found total reviews in header: {count:,} (from: '{text}')")
                                results['total_reviews'] = count
                except:
                    continue
        except Exception as e:
            print(f"Strategy 3 failed: {e}")

        # Strategy 4: Look in page content for review mentions
        try:
            # Get all text elements
            all_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '리뷰') or contains(text(), '방문자') or contains(text(), '블로그')]")

            for elem in all_elements:
                try:
                    text = elem.text.strip()
                    if not text:
                        continue

                    # Check for visitor review patterns
                    if '방문자' in text and results['visitor_reviews'] == 0:
                        count = extract_number(text)
                        if count > 0:
                            results['visitor_reviews'] = count
                            print(f"✓ Found visitor reviews (content scan): {count:,} (from: '{text}')")

                    # Check for blog review patterns
                    if '블로그' in text and results['blog_reviews'] == 0:
                        count = extract_number(text)
                        if count > 0:
                            results['blog_reviews'] = count
                            print(f"✓ Found blog reviews (content scan): {count:,} (from: '{text}')")

                    # Check for total review patterns
                    if '리뷰' in text:
                        count = extract_number(text)
                        if count > results['total_reviews']:
                            results['total_reviews'] = count
                            print(f"✓ Found total reviews (content scan): {count:,} (from: '{text}')")
                except:
                    continue
        except Exception as e:
            print(f"Strategy 4 failed: {e}")

        # Strategy 5: Try specific Naver Place class names
        try:
            class_patterns = [
                "place_section_count",
                "place_review_count",
                "Review_count",
                "review_count_num",
                "place_section_num"
            ]

            for pattern in class_patterns:
                try:
                    elements = driver.find_elements(By.XPATH, f"//*[contains(@class, '{pattern}')]")
                    for elem in elements:
                        text = elem.text.strip()
                        count = extract_number(text)
                        if count > 0:
                            parent_text = elem.find_element(By.XPATH, "..").text if elem else ""
                            if '방문자' in parent_text and results['visitor_reviews'] == 0:
                                results['visitor_reviews'] = count
                                print(f"✓ Found visitor reviews (class): {count:,}")
                            elif '블로그' in parent_text and results['blog_reviews'] == 0:
                                results['blog_reviews'] = count
                                print(f"✓ Found blog reviews (class): {count:,}")
                except:
                    continue
        except Exception as e:
            print(f"Strategy 5 failed: {e}")

        # Calculate total if not found directly
        if results['total_reviews'] == 0:
            calculated_total = results['visitor_reviews'] + results['blog_reviews']
            if calculated_total > 0:
                results['total_reviews'] = calculated_total
                print(f"\n✓ Calculated total reviews: {calculated_total:,} (visitor + blog)")

        # Verify total is at least the sum of parts
        sum_of_parts = results['visitor_reviews'] + results['blog_reviews']
        if sum_of_parts > results['total_reviews']:
            results['total_reviews'] = sum_of_parts

        print("\n=== Extraction Complete ===\n")

        # Save page source for debugging if needed
        if results['total_reviews'] == 0:
            print("WARNING: No reviews found. Page source preview:")
            print(driver.page_source[:1000])
            print("\n... (truncated)")

        return results

    except Exception as e:
        print(f"\n❌ Error during crawling: {e}")
        import traceback
        traceback.print_exc()
        return {
            'url': url,
            'error': str(e),
            'total_reviews': 0,
            'visitor_reviews': 0,
            'blog_reviews': 0
        }
    finally:
        if driver:
            driver.quit()


def main():
    """Main function to run the crawler"""
    # Target URL
    url = "https://m.place.naver.com/restaurant/1672120714/review/visitor"

    print("=" * 60)
    print("Naver Place Review Crawler")
    print("=" * 60)
    print(f"Target: {url}\n")

    results = crawl_naver_place_reviews(url)

    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"URL: {results['url']}")
    print(f"Total Reviews: {results['total_reviews']:,}")
    print(f"Visitor Reviews: {results['visitor_reviews']:,}")
    print(f"Blog Reviews: {results['blog_reviews']:,}")
    print("=" * 60)

    if results['total_reviews'] == 0:
        print("\n⚠ WARNING: No review data was extracted.")
        print("This could mean:")
        print("  1. The page structure has changed")
        print("  2. The page requires login or additional interaction")
        print("  3. Network/loading issues occurred")
        print("\nCheck the debug output above for more details.")

    return results


if __name__ == "__main__":
    main()
