#!/usr/bin/env python3
"""
Bulk Enhanced Workflow with Resume Capability
============================================

Runs the enhanced workflow on all products from Pricing_Exp.xlsx
with the ability to resume from where it left off if interrupted.
"""

import pandas as pd
import asyncio
import time
import json
import os
from typing import List, Dict, Optional
from trolley_scraper_fixed import FixedTrolleyScraper
from enhanced_matcher import EnhancedProductMatcher
from cache_manager import CacheManager

# Progress tracking file
PROGRESS_FILE = "bulk_processing_progress.json"
RESULTS_FILE = "enhanced_matching_results.csv"

def load_progress() -> Dict:
    """Load progress from file"""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"completed_products": [], "results": [], "last_product_index": 0}

def save_progress(progress: Dict):
    """Save progress to file"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

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

def run_bulk_with_resume():
    """Run enhanced workflow for all products with resume capability"""
    
    print("🚀 Bulk Enhanced Product Matching Workflow (with Resume)")
    print("=" * 70)
    print("🎯 Preferred Retailers (in order):")
    print("   1. 🥇 Tesco")
    print("   2. 🥈 Ocado") 
    print("   3. 🥉 Morrisons")
    print("   4. 4️⃣ Sainsbury's")
    print("📁 Reading products from Pricing Exp.xlsx...")
    
    # Load progress
    progress = load_progress()
    completed_products = set(progress.get("completed_products", []))
    all_results = progress.get("results", [])
    last_product_index = progress.get("last_product_index", 0)
    
    # Read all products from Excel
    product_names = read_products_from_excel()
    
    if not product_names:
        print("❌ No products found in Excel file")
        return
    
    # Filter out already completed products
    remaining_products = [p for p in product_names if p not in completed_products]
    
    print(f"\n📊 Progress Summary:")
    print(f"   Total Products: {len(product_names)}")
    print(f"   Already Completed: {len(completed_products)}")
    print(f"   Remaining: {len(remaining_products)}")
    print(f"   Last Processed Index: {last_product_index}")
    
    if not remaining_products:
        print("✅ All products already processed!")
        return
    
    print(f"\n🎯 Processing {len(remaining_products)} remaining products...")
    print("⚠️  Note: Cache is disabled - fresh scraping for each product")
    print("💾 Progress will be saved automatically")
    
    # Ask user if they want to continue
    response = input(f"\nContinue with {len(remaining_products)} remaining products? (y/n): ").strip().lower()
    if response != 'y':
        print("❌ Cancelled by user")
        return
    
    successful_matches = 0
    failed_matches = 0
    
    # Process each remaining product
    for i, product_name in enumerate(remaining_products, 1):
        current_index = last_product_index + i
        
        print(f"\n{'='*70}")
        print(f"📦 Processing {current_index}/{len(product_names)}: {product_name}")
        print(f"{'='*70}")
        
        try:
            # Run enhanced workflow for this product
            matches = run_enhanced_workflow_no_cache(product_name)
            
            if matches:
                all_results.extend(matches)
                successful_matches += 1
                print(f"✅ Successfully processed: {product_name}")
            else:
                failed_matches += 1
                print(f"❌ No matches found: {product_name}")
            
            # Mark as completed
            completed_products.add(product_name)
            
            # Update progress
            progress["completed_products"] = list(completed_products)
            progress["results"] = all_results
            progress["last_product_index"] = current_index
            save_progress(progress)
            
            # Save results to CSV periodically
            if i % 10 == 0:  # Save every 10 products
                try:
                    df_results = pd.DataFrame(all_results)
                    df_results.to_csv(RESULTS_FILE, index=False)
                    print(f"💾 Progress saved to {RESULTS_FILE}")
                except Exception as e:
                    print(f"⚠️  Warning: Could not save results: {e}")
            
        except KeyboardInterrupt:
            print(f"\n⚠️  Process interrupted at product {current_index}")
            print(f"💾 Progress saved. You can resume later.")
            return
        except Exception as e:
            print(f"❌ Error processing {product_name}: {e}")
            failed_matches += 1
            # Still mark as completed to avoid infinite retry
            completed_products.add(product_name)
            progress["completed_products"] = list(completed_products)
            save_progress(progress)
        
        # Add delay between requests to be respectful
        if i < len(remaining_products):
            print("⏳ Waiting 2 seconds before next product...")
            time.sleep(2)
    
    # Print final summary
    print(f"\n{'='*70}")
    print("📊 BULK PROCESSING SUMMARY")
    print(f"{'='*70}")
    print(f"Total Products: {len(product_names)}")
    print(f"Successfully Processed: {successful_matches}")
    print(f"Failed Matches: {failed_matches}")
    print(f"Success Rate: {(successful_matches/len(product_names)*100):.1f}%")
    print(f"Total Enhanced Matches Found: {len(all_results)}")
    
    # Save final results to CSV
    if all_results:
        try:
            df_results = pd.DataFrame(all_results)
            df_results.to_csv(RESULTS_FILE, index=False)
            print(f"\n💾 Final results saved to: {RESULTS_FILE}")
            
            # Show sample of results
            print(f"\n📋 Sample Results (first 5):")
            print(df_results.head().to_string(index=False))
            
        except Exception as e:
            print(f"❌ Error saving final results: {e}")
    
    # Clean up progress file
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)
        print(f"🧹 Progress file cleaned up")
    
    print(f"\n✅ Bulk processing completed!")

if __name__ == "__main__":
    run_bulk_with_resume()
