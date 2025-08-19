#!/usr/bin/env python3
"""
Debug script to see what search terms are generated for Heinz multipack
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scraper'))

from scraper.trolley_scraper_fixed import FixedTrolleyScraper

def debug_heinz_search_terms():
    """Debug the search terms generated for Heinz multipack"""
    print("🔍 Debugging Heinz multipack search terms")
    print("=" * 50)
    
    # Initialize scraper
    scraper = FixedTrolleyScraper()
    
    # Test product
    product_name = "Heinz Beanz 6 x 415g"
    
    print(f"📝 Product: {product_name}")
    print(f"🔍 Is multipack: {scraper._is_multipack(product_name)}")
    
    # Get search terms
    search_terms = scraper._generate_search_terms(product_name)
    
    print(f"\n🔍 Generated search terms ({len(search_terms)}):")
    for i, term in enumerate(search_terms, 1):
        print(f"{i}. {term}")
    
    # Test each search term
    print(f"\n🧪 Testing each search term:")
    for i, search_term in enumerate(search_terms, 1):
        print(f"\n{i}. Testing: '{search_term}'")
        
        # Create search URL
        search_url = f"https://www.trolley.co.uk/search?q={search_term}"
        print(f"   URL: {search_url}")
        
        try:
            # Get search results
            response = scraper.session.get(search_url)
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract product cards
                cards = scraper._extract_product_cards(soup)
                print(f"   Found {len(cards)} product cards")
                
                # Check first few cards for Heinz products
                heinz_cards = []
                for j, card in enumerate(cards[:5]):  # Check first 5 cards
                    card_text = card.get_text().lower()
                    if "heinz" in card_text:
                        product_name_from_card = scraper._extract_product_name_from_card(card)
                        similarity = scraper._calculate_similarity_improved(product_name_from_card, product_name)
                        heinz_cards.append((product_name_from_card, similarity))
                
                if heinz_cards:
                    print(f"   Heinz products found:")
                    for name, similarity in heinz_cards:
                        print(f"     - {name} (similarity: {similarity:.3f})")
                else:
                    print(f"   No Heinz products found in first 5 cards")
                    
            else:
                print(f"   ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    debug_heinz_search_terms()
