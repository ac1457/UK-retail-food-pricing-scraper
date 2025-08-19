#!/usr/bin/env python3
"""
Test Branston fix
"""

from trolley_scraper_fixed import FixedTrolleyScraper

def test_branston():
    """Test Branston product matching"""
    print("🧪 Testing Branston fix")
    print("=" * 40)
    
    scraper = FixedTrolleyScraper()
    scraper.clear_cache()
    
    # Test the problematic product
    product = "Branston Baked Beans 4 x 410g"
    print(f"🔍 Testing: {product}")
    
    results = scraper.search_product(product)
    
    if results:
        print(f"✅ Found {len(results)} results")
        for i, result in enumerate(results[:5], 1):  # Show top 5
            print(f"  {i}. {result['name']} (Score: {result['similarity_score']:.3f})")
            print(f"     URL: {result['url']}")
            if result['retailer_prices']:
                prices = []
                for retailer, price_info in result['retailer_prices'].items():
                    prices.append(f"{retailer}: £{price_info['price']}")
                print(f"     Prices: {', '.join(prices)}")
            print()
        
        best = max(results, key=lambda x: x['similarity_score'])
        print(f"🏆 Best match: {best['name']} (Score: {best['similarity_score']:.3f})")
        print(f"   URL: {best['url']}")
        
        # Check if it's the correct product (should NOT be reduced sugar/salt)
        if "reduced" in best['name'].lower():
            print("❌ ERROR: Still matching reduced sugar/salt variant!")
        else:
            print("✅ SUCCESS: Matching correct regular variant!")
    else:
        print("❌ No results found")

if __name__ == "__main__":
    test_branston()
