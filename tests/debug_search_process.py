#!/usr/bin/env python3
"""
Debug the search process to see why the wrong product is being found
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scraper'))

from scraper.trolley_scraper_fixed import FixedTrolleyScraper

def debug_search_process():
    """Debug the search process step by step"""
    print("🔍 Debugging search process for Heinz multipack")
    print("=" * 60)
    
    # Initialize scraper
    scraper = FixedTrolleyScraper()
    scraper.clear_cache()
    
    product_name = "Heinz Beanz 6 x 415g"
    print(f"📝 Product: {product_name}")
    
    # Get search terms
    search_terms = scraper._generate_search_terms(product_name)
    print(f"\n🔍 Generated search terms: {search_terms}")
    
    # Test the first search term in detail
    search_term = search_terms[0]  # "Heinz Family Pack"
    print(f"\n🧪 Testing search term: '{search_term}'")
    
    # Create search URL
    search_url = f"https://www.trolley.co.uk/search?q={search_term}"
    print(f"🔗 Search URL: {search_url}")
    
    try:
        # Get search results
        response = scraper.session.get(search_url)
        if response.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract product cards
            cards = scraper._extract_product_cards(soup)
            print(f"📦 Found {len(cards)} product cards")
            
            # Check first 10 cards for Heinz products
            heinz_cards = []
            for i, card in enumerate(cards[:10]):
                card_text = card.get_text().lower()
                if "heinz" in card_text:
                    product_name_from_card = scraper._extract_product_name_from_card(card)
                    similarity = scraper._calculate_similarity_improved(product_name_from_card, product_name)
                    url = scraper._extract_product_url(card)
                    
                    heinz_cards.append({
                        'index': i,
                        'name': product_name_from_card,
                        'similarity': similarity,
                        'url': url,
                        'raw_text': card.get_text()[:100] + "..."
                    })
            
            print(f"\n🔍 Heinz products found in first 10 cards:")
            for card_info in heinz_cards:
                print(f"\n  Card {card_info['index']}:")
                print(f"    Name: {card_info['name']}")
                print(f"    Similarity: {card_info['similarity']:.3f}")
                print(f"    URL: {card_info['url']}")
                print(f"    Raw text: {card_info['raw_text']}")
                
                # Check if this is the correct product
                if "heinz-beanz-family-pack" in card_info['url']:
                    print(f"    ✅ CORRECT PRODUCT!")
                else:
                    print(f"    ❌ Wrong product")
            
            # Check if correct URL was found
            correct_found = any("heinz-beanz-family-pack" in card['url'] for card in heinz_cards)
            
            if correct_found:
                print(f"\n🎉 SUCCESS: Correct Heinz Family Pack found in search results!")
            else:
                print(f"\n❌ FAILURE: Correct Heinz Family Pack NOT found in search results")
                print(f"Expected URL: https://www.trolley.co.uk/product/heinz-beanz-family-pack/DJC713")
                
        else:
            print(f"❌ HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_search_process()
