#!/usr/bin/env python3
"""
Example usage of the Naver Restaurant Scraper

This script demonstrates how to use the NaverRestaurantScraper class
to retrieve restaurant data from Naver Maps and Naver Place.
"""

from naver_restaurant_scraper import NaverRestaurantScraper
import json


def example_1_basic_usage():
    """Example 1: Basic usage with default restaurant"""
    print("\n" + "="*60)
    print("Example 1: Basic Usage")
    print("="*60)

    scraper = NaverRestaurantScraper()
    data = scraper.search_restaurant("Namaste Wangsimni Branch")
    scraper.display_results(data)


def example_2_multiple_restaurants():
    """Example 2: Search multiple restaurants"""
    print("\n" + "="*60)
    print("Example 2: Multiple Restaurants")
    print("="*60)

    restaurants = [
        "Namaste Wangsimni Branch",
        "신당동 떡볶이",
        "광장시장 마약김밥"
    ]

    scraper = NaverRestaurantScraper()

    results = []
    for restaurant_name in restaurants:
        print(f"\nSearching for: {restaurant_name}")
        data = scraper.search_restaurant(restaurant_name)
        if data:
            results.append(data)
            print(f"✓ Found: {data['place_id']}")
        else:
            print(f"✗ Not found")

    # Display summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    for result in results:
        print(f"\n{result['restaurant_name']}")
        print(f"  - Reviews: {result['visitor_reviews']} visitor, {result['blog_reviews']} blog")
        print(f"  - Rating: {result['naver_rating']}")


def example_3_json_output():
    """Example 3: Get JSON output for API integration"""
    print("\n" + "="*60)
    print("Example 3: JSON Output")
    print("="*60)

    scraper = NaverRestaurantScraper()
    data = scraper.search_restaurant("Namaste Wangsimni Branch")

    if data:
        # Convert to JSON
        json_output = json.dumps(data, ensure_ascii=False, indent=2)
        print("\nJSON Format:")
        print(json_output)

        # Save to file
        with open('restaurant_data.json', 'w', encoding='utf-8') as f:
            f.write(json_output)
        print("\n✓ Data saved to restaurant_data.json")


def example_4_data_validation():
    """Example 4: Validate and use specific data fields"""
    print("\n" + "="*60)
    print("Example 4: Data Validation")
    print("="*60)

    scraper = NaverRestaurantScraper()
    data = scraper.search_restaurant("Namaste Wangsimni Branch")

    if data:
        # Check if rating exists
        if data['naver_rating'] is not None:
            print(f"✓ Restaurant has rating: {data['naver_rating']}")
            if data['naver_rating'] >= 4.0:
                print("  → Highly rated!")
        else:
            print("✗ No rating available")

        # Check if AI briefing exists
        if data['ai_briefing']:
            print(f"\n✓ AI Briefing available:")
            print(f"  {data['ai_briefing'][:100]}...")
        else:
            print("\n✗ No AI Briefing available")

        # Check review counts
        total_reviews = (data['visitor_reviews'] or 0) + (data['blog_reviews'] or 0)
        print(f"\n✓ Total reviews: {total_reviews}")


def main():
    """Run all examples"""
    print("\n" + "#"*60)
    print("# Naver Restaurant Scraper - Example Usage")
    print("#"*60)

    # Run examples
    example_1_basic_usage()

    # Uncomment to run other examples:
    # example_2_multiple_restaurants()
    # example_3_json_output()
    # example_4_data_validation()


if __name__ == "__main__":
    main()
