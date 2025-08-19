#!/usr/bin/env python3
"""
Debug Heinz Multipack Price Issue
================================
Debug why Heinz Beanz 6 x 415g is not finding prices
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper.trolley_scraper_fixed import FixedTrolleyScraper


def debug_heinz_multipack_price():
    """Debug the Heinz multipack price issue"""
    print("🔍 Debugging Heinz Multipack Price Issue")
    print("=" * 60)
    
    scraper = FixedTrolleyScraper(clear_cache=True)
    
    # The specific product that's failing
    product_name = "Heinz Beanz 6 x 415g"
    
    print(f"🔍 Testing product: {product_name}")
    print()
    
    # Test 1: Check quantity extraction
    print("📦 Step 1: Quantity Extraction")
    quantity, pack_size = scraper._extract_quantity_and_pack_size(product_name)
    print(f"  Quantity: {quantity}")
    print(f"  Pack size: {pack_size}")
    print()
    
    # Test 2: Check search term generation
    print("🔍 Step 2: Search Term Generation")
    search_terms = scraper._generate_search_terms(product_name)
    print(f"  Generated search terms: {search_terms}")
    print()
    
    # Test 3: Perform actual search
    print("🌐 Step 3: Performing Search")
    results = scraper.search_product(product_name)
    
    if results:
        print(f"  ✅ Found {len(results)} results")
        for i, result in enumerate(results[:3], 1):  # Show first 3 results
            print(f"    {i}. {result['name']}")
            print(f"       Similarity: {result['similarity_score']:.3f}")
            print(f"       URL: {result['url'][:80]}...")
            
            # Check if it has retailer prices
            if result.get('retailer_prices'):
                print(f"       Retailers found: {list(result['retailer_prices'].keys())}")
                for retailer, price_info in result['retailer_prices'].items():
                    print(f"         {retailer}: £{price_info.get('price', 'N/A')}")
            else:
                print(f"       ❌ No retailer prices found")
            print()
    else:
        print(f"  ❌ No search results found")
        print()
    
    # Test 4: Check if the issue is with price extraction
    if results:
        best_match = max(results, key=lambda x: x['similarity_score'])
        print("💰 Step 4: Price Extraction Analysis")
        print(f"  Best match: {best_match['name']}")
        print(f"  URL: {best_match['url']}")
        
        if best_match.get('retailer_prices'):
            print(f"  ✅ Retailer prices found: {list(best_match['retailer_prices'].keys())}")
        else:
            print(f"  ❌ No retailer prices in best match")
            print(f"  🔍 This suggests the price extraction failed")
    
    # Test 5: Try alternative search terms
    print("\n🔄 Step 5: Alternative Search Terms")
    alternative_terms = [
        "Heinz Beanz 6x415g",
        "Heinz Beanz 6 pack",
        "Heinz Beanz multipack",
        "Heinz Five Beanz 6 x 415g",
        "Heinz Beanz in Tomato Sauce 6 x 415g"
    ]
    
    for term in alternative_terms:
        print(f"  Testing: {term}")
        alt_results = scraper.search_product(term)
        if alt_results:
            best_alt = max(alt_results, key=lambda x: x['similarity_score'])
            print(f"    ✅ Found: {best_alt['name']} (score: {best_alt['similarity_score']:.3f})")
            if best_alt.get('retailer_prices'):
                retailers = list(best_alt['retailer_prices'].keys())
                print(f"    💰 Retailers: {retailers}")
            else:
                print(f"    ❌ No prices")
        else:
            print(f"    ❌ No results")
        print()
    
    # Test 6: Check if it's a multipack vs single issue
    print("📦 Step 6: Multipack vs Single Comparison")
    single_product = "Heinz Beanz 415g"
    
    single_results = scraper.search_product(single_product)
    if single_results:
        best_single = max(single_results, key=lambda x: x['similarity_score'])
        print(f"  Single product '{single_product}':")
        print(f"    Found: {best_single['name']} (score: {best_single['similarity_score']:.3f})")
        if best_single.get('retailer_prices'):
            retailers = list(best_single['retailer_prices'].keys())
            print(f"    💰 Retailers: {retailers}")
        else:
            print(f"    ❌ No prices")
    
    print("\n🎯 Summary:")
    print("  If no search results found: The product might not exist on Trolley.co.uk")
    print("  If search results found but no prices: Price extraction is failing")
    print("  If single product works but multipack doesn't: Multipack matching issue")
    print("  If alternative terms work: Search term generation needs improvement")


if __name__ == "__main__":
    debug_heinz_multipack_price()
