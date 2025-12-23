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


def setup_driver():
    """Set up Chrome driver with options suitable for Colab"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36')

    driver = webdriver.Chrome(options=chrome_options)
    return driver


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

        # Wait for page to load
        time.sleep(3)

        results = {
            'url': url,
            'total_reviews': 0,
            'visitor_reviews': 0,
            'blog_reviews': 0
        }

        # Try to find review count elements
        # Naver Place uses various selectors for review counts
        try:
            # Wait for the page to load review elements
            wait = WebDriverWait(driver, 10)

            # Try to find visitor review count
            # Common patterns in Naver Place mobile pages
            try:
                # Look for tab elements that show counts
                visitor_tab = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/review/visitor')]"))
                )
                visitor_text = visitor_tab.text
                print(f"Visitor tab text: {visitor_text}")

                # Extract number from text like "방문자리뷰 1234" or "방문자 (1234)"
                import re
                visitor_match = re.search(r'(\d+(?:,\d+)*)', visitor_text)
                if visitor_match:
                    results['visitor_reviews'] = int(visitor_match.group(1).replace(',', ''))
            except Exception as e:
                print(f"Could not find visitor reviews: {e}")

            # Try to find blog review count
            try:
                blog_tab = driver.find_element(By.XPATH, "//a[contains(@href, '/review/ugc')]")
                blog_text = blog_tab.text
                print(f"Blog tab text: {blog_text}")

                import re
                blog_match = re.search(r'(\d+(?:,\d+)*)', blog_text)
                if blog_match:
                    results['blog_reviews'] = int(blog_match.group(1).replace(',', ''))
            except Exception as e:
                print(f"Could not find blog reviews: {e}")

            # Calculate total
            results['total_reviews'] = results['visitor_reviews'] + results['blog_reviews']

            # Alternative: try to find a total count element
            try:
                # Look for elements with class or text containing review count
                review_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '리뷰')]")
                for element in review_elements:
                    text = element.text
                    print(f"Found review element: {text}")

                    # Look for patterns like "리뷰 1,234"
                    import re
                    total_match = re.search(r'리뷰\s*(\d+(?:,\d+)*)', text)
                    if total_match:
                        potential_total = int(total_match.group(1).replace(',', ''))
                        if potential_total > results['total_reviews']:
                            results['total_reviews'] = potential_total
            except Exception as e:
                print(f"Could not find total reviews: {e}")

        except Exception as e:
            print(f"Error finding review counts: {e}")

        # Print page source for debugging (first 500 chars)
        print("\n=== Page Source Preview ===")
        print(driver.page_source[:500])

        return results

    except Exception as e:
        print(f"Error during crawling: {e}")
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

    results = crawl_naver_place_reviews(url)

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"URL: {results['url']}")
    print(f"Total Reviews: {results['total_reviews']:,}")
    print(f"Visitor Reviews: {results['visitor_reviews']:,}")
    print(f"Blog Reviews: {results['blog_reviews']:,}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    main()
