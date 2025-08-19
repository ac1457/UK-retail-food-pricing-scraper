#!/usr/bin/env python3
"""
Test general multipack issue
"""

from trolley_scraper_fixed import FixedTrolleyScraper

def test_multipack_general():
    """Test general multipack matching"""
    print("🧪 Testing General Multipack Issue")
    print("=" * 50)
    
    scraper = FixedTrolleyScraper()
    scraper.clear_cache()
    
    # Test multiple multipack products
    test_products = [
        "Heinz Cream of Tomato Soup 4 x 400g",
        "Branston Baked Beans 4 x 410g",
        "Heinz Beanz 6 x 415g"
    ]
    
    for product in test_products:
        print(f"\n🔍 Testing: {product}")
        print("-" * 40)
        
        # Check if it's detected as multipack
        is_multipack = scraper._is_multipack(product)
        print(f"   Is multipack: {is_multipack}")
        
        # Check quantity extraction
        quantity, pack_size = scraper._extract_quantity_and_pack_size(product)
        print(f"   Quantity: {quantity}, Pack size: {pack_size}")
        
        # Check brand extraction
        brand, product_name = scraper._extract_brand_and_product(product)
        print(f"   Brand: '{brand}', Product: '{product_name}'")
        
        # Generate search terms
        search_terms = scraper._generate_search_terms(product)
        print(f"   Search terms: {search_terms}")
        
        # Test actual search
        results = scraper.search_product(product)
        
        if results:
            print(f"   ✅ Found {len(results)} results")
            best = max(results, key=lambda x: x['similarity_score'])
            print(f"   🏆 Best match: {best['name']} (Score: {best['similarity_score']:.3f})")
            print(f"      URL: {best['url']}")
            
            # Check if it's a multipack match
            if scraper._is_multipack(best['name']):
                print(f"      ✅ Correctly matched multipack")
            else:
                print(f"      ❌ ERROR: Matched single product instead of multipack!")
        else:
            print(f"   ❌ No results found")

if __name__ == "__main__":
    test_multipack_general()
