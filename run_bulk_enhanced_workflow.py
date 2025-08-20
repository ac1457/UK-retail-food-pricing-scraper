#!/usr/bin/env python3
"""
Bulk Enhanced Workflow Runner
============================

Reads all products from Pricing_Exp.xlsx and runs the enhanced workflow
for each product without using cached prices.
"""

import pandas as pd
import asyncio
import time
from typing import List, Dict, Optional
from trolley_scraper_fixed import FixedTrolleyScraper
from enhanced_matcher import EnhancedProductMatcher
from cache_manager import CacheManager


def read_products_from_excel(file_path: str = "Pricing Exp.xlsx") -> List[str]:
    """Read product names from the Excel file"""
    try:
        # Read the Excel file
        df = pd.read_excel(file_path)
        
        # Get product names from the Product_Name column
        if 'Product_Name' in df.columns:
            product_names = df['Product_Name'].dropna().tolist()
        else:
            # If column name is different, try to find it
            possible_columns = ['Product Name', 'Product', 'Name', 'Description']
            product_names = []
            for col in possible_columns:
                if col in df.columns:
                    product_names = df[col].dropna().tolist()
                    break
            
            if not product_names:
                # If no matching column found, use the first column
                product_names = df.iloc[:, 0].dropna().tolist()
        
        print(f"📋 Loaded {len(product_names)} products from {file_path}")
        return product_names
        
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return []


def run_enhanced_workflow_no_cache(product_name: str) -> List[Dict]:
    """Run enhanced workflow for a single product without using cache"""
    
    # Initialize the enhanced matcher
    matcher = EnhancedProductMatcher()
    
    # Initialize the trolley scraper with 0 cache duration (no caching)
    scraper = FixedTrolleyScraper(cache_duration_hours=0)
    
    enhanced_matches = []
    
    # Define preferred retailers in order of preference
    preferred_retailers = ['Tesco', 'Ocado', 'Morrisons', 'Sainsbury\'s']
    
    try:
        print(f"🔍 Searching for: {product_name}")
        
        # Step 1: Use the trolley scraper (no cache)
        results = scraper.search_product(product_name)
        
        if not results:
            print(f"❌ No results found for: {product_name}")
            return []
        
        print(f"📋 Found {len(results)} results from trolley scraper")
        
        # Step 2: Apply enhanced matching to each result
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
                        'product_name': product_name,
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
        
        # Step 3: Sort results by retailer preference and confidence
        if enhanced_matches:
            def sort_key(match):
                retailer = match['retailer']
                # Get retailer preference index (lower = higher preference)
                try:
                    retailer_index = preferred_retailers.index(retailer)
                except ValueError:
                    retailer_index = 999  # Put non-preferred retailers at the end
                
                # Sort by retailer preference first, then by confidence
                return (retailer_index, -match['confidence'])
            
            enhanced_matches.sort(key=sort_key)
            
            print(f"✅ Found {len(enhanced_matches)} enhanced matches (sorted by preference):")
            
            for i, match in enumerate(enhanced_matches, 1):
                confidence = match['confidence']
                retailer = match['retailer']
                
                # Check if this is a preferred retailer
                if retailer in preferred_retailers:
                    preference_index = preferred_retailers.index(retailer)
                    preference_emoji = ["🥇", "🥈", "🥉", "4️⃣"][preference_index] if preference_index < 4 else "🏪"
                else:
                    preference_emoji = "🏪"
                
                confidence_emoji = "🟢" if confidence >= 0.8 else "🟡" if confidence >= 0.6 else "🔴"
                
                print(f"\n{i}. {preference_emoji} {match['retailer']} {confidence_emoji}")
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
            print(f"❌ No enhanced matches found for: {product_name}")
            
    except Exception as e:
        print(f"❌ Error processing {product_name}: {e}")
    
    return enhanced_matches


def run_bulk_enhanced_workflow():
    """Run enhanced workflow for all products in the Excel file"""
    
    print("🚀 Bulk Enhanced Product Matching Workflow")
    print("=" * 60)
    print("🎯 Preferred Retailers (in order):")
    print("   1. 🥇 Tesco")
    print("   2. 🥈 Ocado") 
    print("   3. 🥉 Morrisons")
    print("   4. 4️⃣ Sainsbury's")
    print("📁 Reading products from Pricing Exp.xlsx...")
    
    # Read all products from Excel
    product_names = read_products_from_excel()
    
    if not product_names:
        print("❌ No products found in Excel file")
        return
    
    print(f"\n🎯 Processing {len(product_names)} products...")
    print("⚠️  Note: Cache is disabled - fresh scraping for each product")
    
    # Ask user if they want to continue
    response = input(f"\nContinue with {len(product_names)} products? (y/n): ").strip().lower()
    if response != 'y':
        print("❌ Cancelled by user")
        return
    
    all_results = []
    successful_matches = 0
    failed_matches = 0
    
    # Process each product
    for i, product_name in enumerate(product_names, 1):
        print(f"\n{'='*60}")
        print(f"📦 Processing {i}/{len(product_names)}: {product_name}")
        print(f"{'='*60}")
        
        # Run enhanced workflow for this product
        matches = run_enhanced_workflow_no_cache(product_name)
        
        if matches:
            all_results.extend(matches)
            successful_matches += 1
            print(f"✅ Successfully processed: {product_name}")
        else:
            failed_matches += 1
            print(f"❌ No matches found: {product_name}")
        
        # Add delay between requests to be respectful
        if i < len(product_names):
            print("⏳ Waiting 2 seconds before next product...")
            time.sleep(2)
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 BULK PROCESSING SUMMARY")
    print(f"{'='*60}")
    print(f"Total Products: {len(product_names)}")
    print(f"Successful Matches: {successful_matches}")
    print(f"Failed Matches: {failed_matches}")
    print(f"Success Rate: {(successful_matches/len(product_names)*100):.1f}%")
    print(f"Total Enhanced Matches Found: {len(all_results)}")
    
    # Save results to CSV
    if all_results:
        try:
            df_results = pd.DataFrame(all_results)
            output_file = "enhanced_matching_results.csv"
            df_results.to_csv(output_file, index=False)
            print(f"\n💾 Results saved to: {output_file}")
            
            # Show sample of results
            print(f"\n📋 Sample Results (first 5):")
            print(df_results.head().to_string(index=False))
            
        except Exception as e:
            print(f"❌ Error saving results: {e}")
    
    print(f"\n✅ Bulk processing completed!")


def run_single_product_test():
    """Test with a single product from the Excel file"""
    
    print("🧪 Single Product Test")
    print("=" * 40)
    
    # Read products from Excel
    product_names = read_products_from_excel()
    
    if not product_names:
        print("❌ No products found in Excel file")
        return
    
    # Show first few products
    print(f"\n📋 First 5 products from Excel:")
    for i, product in enumerate(product_names[:5], 1):
        print(f"{i}. {product}")
    
    # Let user choose a product
    try:
        choice = int(input(f"\nChoose a product (1-{min(5, len(product_names))}): ")) - 1
        if 0 <= choice < len(product_names):
            selected_product = product_names[choice]
            print(f"\n🎯 Testing with: {selected_product}")
            
            # Run enhanced workflow for this product
            matches = run_enhanced_workflow_no_cache(selected_product)
            
            if matches:
                print(f"\n✅ Found {len(matches)} matches for {selected_product}")
            else:
                print(f"\n❌ No matches found for {selected_product}")
        else:
            print("❌ Invalid choice")
    except ValueError:
        print("❌ Invalid input")


def main():
    """Main function"""
    
    print("🎯 Bulk Enhanced Product Matching Workflow")
    print("Choose an option:")
    print("1. Test with single product from Excel")
    print("2. Run bulk processing for all products")
    print("3. Show products from Excel file")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        run_single_product_test()
    elif choice == "2":
        run_bulk_enhanced_workflow()
    elif choice == "3":
        product_names = read_products_from_excel()
        if product_names:
            print(f"\n📋 Found {len(product_names)} products:")
            for i, product in enumerate(product_names[:10], 1):
                print(f"{i}. {product}")
            if len(product_names) > 10:
                print(f"... and {len(product_names) - 10} more")
    else:
        print("Invalid choice. Running single product test...")
        run_single_product_test()


if __name__ == "__main__":
    main()
