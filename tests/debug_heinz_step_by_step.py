#!/usr/bin/env python3
"""
Detailed debug script to trace Heinz search step by step
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scraper'))

from scraper.trolley_scraper_fixed import FixedTrolleyScraper

def debug_heinz_step_by_step():
    """Debug Heinz search step by step"""
    print("🔍 Debugging Heinz search step by step")
    print("=" * 60)
    
    # Initialize scraper
    scraper = FixedTrolleyScraper()
    scraper.clear_cache()
    
    product_name = "Heinz Beanz 6 x 415g"
    print(f"📝 Original product: {product_name}")
    
    # Step 1: Check if it's detected as multipack
    is_multipack = scraper._is_multipack(product_name)
    print(f"\n1️⃣ Is multipack: {is_multipack}")
    
    # Step 2: Extract brand and product
    brand, product = scraper._extract_brand_and_product(product_name)
    print(f"\n2️⃣ Brand: '{brand}' | Product: '{product}'")
    
    # Step 3: Generate search terms
    search_terms = scraper._generate_search_terms(product_name)
    print(f"\n3️⃣ Generated search terms:")
    for i, term in enumerate(search_terms, 1):
        print(f"   {i}. {term}")
    
    # Step 4: Test the most specific search term first
    specific_term = "Heinz Baked Beans Family Pack"
    print(f"\n4️⃣ Testing specific search: '{specific_term}'")
    
    search_url = f"https://www.trolley.co.uk/search?q={specific_term}"
    print(f"   URL: {search_url}")
    
    # Get the search results
    response = scraper.session.get(search_url, timeout=30)
    if response.status_code == 200:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract product cards
        product_cards = scraper._extract_product_cards(soup)
        print(f"   Found {len(product_cards)} product cards")
        
        # Check each card
        for i, card in enumerate(product_cards[:5], 1):
            print(f"\n   📦 Card {i}:")
            
            # Extract product name
            extracted_name = scraper._extract_product_name_from_card(card)
            print(f"      Extracted name: '{extracted_name}'")
            
            # Calculate similarity
            similarity = scraper._calculate_similarity_improved(extracted_name, product_name)
            print(f"      Similarity: {similarity:.3f}")
            
            # Extract URL
            url = scraper._extract_product_url(card)
            print(f"      URL: {url}")
            
            # Check if this is the correct product
            if "heinz-beanz-family-pack" in url:
                print(f"      ✅ FOUND CORRECT PRODUCT!")
            elif "heinz" in extracted_name.lower():
                print(f"      ⚠️  Found Heinz product but wrong one")
            else:
                print(f"      ❌ Not a Heinz product")
    else:
        print(f"   ❌ Search failed: HTTP {response.status_code}")

if __name__ == "__main__":
    debug_heinz_step_by_step()
