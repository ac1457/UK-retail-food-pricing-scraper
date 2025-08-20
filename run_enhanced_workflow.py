#!/usr/bin/env python3
"""
Enhanced Workflow Runner
========================

Demonstrates how to use the enhanced product matching system
with the existing trolley scraper workflow.
"""

import asyncio
from trolley_scraper_fixed import FixedTrolleyScraper
from enhanced_matcher import EnhancedProductMatcher
from cache_manager import CacheManager


def run_enhanced_workflow():
    """Run the enhanced workflow with product matching"""
    
    print("🚀 Enhanced Product Matching Workflow")
    print("=" * 50)
    
    # Initialize the enhanced matcher
    matcher = EnhancedProductMatcher()
    
    # Initialize the trolley scraper
    scraper = FixedTrolleyScraper(cache_duration_hours=24)
    
    # Test products to search for
    test_products = [
        "Heinz Baked Beans 415g",
        "Branston Baked Beans 410g", 
        "Tesco Baked Beans 420g",
        "Heinz Cream of Tomato Soup 400g"
    ]
    
    for product_name in test_products:
        print(f"\n🔍 Searching for: {product_name}")
        print("-" * 40)
        
        try:
            # Step 1: Use the existing trolley scraper
            results = scraper.search_product(product_name)
            
            if not results:
                print("❌ No results found from trolley scraper")
                continue
            
            print(f"📋 Found {len(results)} results from trolley scraper")
            
            # Step 2: Apply enhanced matching to each result
            enhanced_matches = []
            
            for result in results:
                # Extract retailer prices
                retailer_prices = result.get('retailer_prices', {})
                
                for retailer, price_data in retailer_prices.items():
                    if not price_data or not isinstance(price_data, dict):
                        continue
                    
                    # Create item for enhanced matching
                    item = {
                        'name': result.get('name', ''),
                        'price': price_data.get('price'),
                        'price_text': price_data.get('price_text', ''),
                        'retailer': retailer,
                        'url': result.get('url')
                    }
                    
                    # Apply enhanced matching
                    match = matcher.enhanced_product_match(product_name, [item], threshold=0.5)
                    
                    if match:
                        enhanced_matches.append({
                            'retailer': retailer,
                            'product': match.name,
                            'price': match.price,
                            'unit_price': match.unit_price,
                            'weight': match.weight,
                            'confidence': match.confidence,
                            'match_type': match.match_type,
                            'validation_issues': match.validation_issues,
                            'url': match.url
                        })
            
            # Step 3: Display enhanced results
            if enhanced_matches:
                print(f"✅ Found {len(enhanced_matches)} enhanced matches:")
                
                # Sort by confidence
                enhanced_matches.sort(key=lambda x: x['confidence'], reverse=True)
                
                for i, match in enumerate(enhanced_matches, 1):
                    confidence = match['confidence']
                    confidence_emoji = "🟢" if confidence >= 0.8 else "🟡" if confidence >= 0.6 else "🔴"
                    
                    print(f"\n{i}. {confidence_emoji} {match['retailer']}")
                    print(f"   Product: {match['product']}")
                    
                    if match['price'] is not None:
                        print(f"   Price: £{match['price']:.2f}")
                    else:
                        print(f"   Price: N/A")
                    
                    if match['unit_price']:
                        print(f"   Unit Price: £{match['unit_price']:.2f}")
                    
                    if match['weight']:
                        print(f"   Weight: {match['weight']}")
                    
                    print(f"   Confidence: {confidence:.2%} ({match['match_type']})")
                    
                    # Show validation issues if any
                    issues = match['validation_issues']
                    if issues:
                        print(f"   ⚠️  Validation Issues:")
                        for issue in issues:
                            print(f"      - {issue}")
                    else:
                        print(f"   ✅ No validation issues")
            else:
                print("❌ No enhanced matches found")
                
        except Exception as e:
            print(f"❌ Error processing {product_name}: {e}")
        
        print("\n" + "=" * 50)


def run_simple_enhanced_test():
    """Run a simple test with sample data"""
    
    print("🧪 Simple Enhanced Matching Test")
    print("=" * 40)
    
    matcher = EnhancedProductMatcher()
    
    # Sample scraped data (simulating what the trolley scraper would return)
    sample_scraped_data = [
        {
            'name': 'Heinz Baked Beans 415g Clubcard Price',
            'price': '£0.85',
            'retailer': 'Tesco'
        },
        {
            'name': 'Heinz Baked Beans 415g',
            'price': '£1.40',
            'retailer': 'Tesco'
        },
        {
            'name': 'Tesco Baked Beans 420g',
            'price': '£0.75',
            'retailer': 'Tesco'
        },
        {
            'name': 'Branston Baked Beans 410g',
            'price': '£0.80',
            'retailer': 'Sainsbury\'s'
        },
        {
            'name': 'Heinz Cream of Tomato Soup 400g',
            'price': '£1.20',
            'retailer': 'ASDA'
        }
    ]
    
    # Test product
    search_product = "Heinz Baked Beans 415g"
    
    print(f"Searching for: {search_product}")
    print(f"Available items: {len(sample_scraped_data)}")
    print()
    
    # Find the best match
    match = matcher.enhanced_product_match(search_product, sample_scraped_data, threshold=0.5)
    
    if match:
        print(f"✅ Best match found!")
        print(f"Product: {match.name}")
        if match.price is not None:
            print(f"Price: £{match.price:.2f}")
        else:
            print(f"Price: N/A")
        print(f"Retailer: {match.retailer}")
        print(f"Confidence: {match.confidence:.2%}")
        print(f"Match type: {match.match_type}")
        
        if match.validation_issues:
            print("⚠️  Validation Issues:")
            for issue in match.validation_issues:
                print(f"   - {issue}")
        else:
            print("✅ No validation issues")
    else:
        print("❌ No match found")


def main():
    """Main function to run the enhanced workflow"""
    
    print("🎯 Enhanced Product Matching Workflow")
    print("Choose an option:")
    print("1. Run simple enhanced test")
    print("2. Run full enhanced workflow with trolley scraper")
    print("3. Run both")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        run_simple_enhanced_test()
    elif choice == "2":
        run_enhanced_workflow()
    elif choice == "3":
        run_simple_enhanced_test()
        print("\n" + "=" * 60)
        run_enhanced_workflow()
    else:
        print("Invalid choice. Running simple test...")
        run_simple_enhanced_test()


if __name__ == "__main__":
    main()
