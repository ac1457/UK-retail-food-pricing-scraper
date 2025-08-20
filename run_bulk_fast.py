#!/usr/bin/env python3
"""
Fast Bulk Enhanced Workflow with Resume Capability
================================================

Runs the enhanced workflow on all products from Pricing_Exp.xlsx
with faster processing and resume capability.
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

def run_enhanced_workflow_fast(product_name: str) -> List[Dict]:
    """Run enhanced workflow for a single product with minimal output"""
    
    # Initialize the enhanced matcher
    matcher = EnhancedProductMatcher()
    
    # Initialize the trolley scraper with 0 cache duration (no caching)
    scraper = FixedTrolleyScraper(cache_duration_hours=0)
    
    enhanced_matches = []
    
    # Define preferred retailers in order of preference
    preferred_retailers = ['Tesco', 'Ocado', 'Morrisons', 'Sainsbury\'s']
    
    try:
        # Step 1: Use the trolley scraper (no cache)
        results = scraper.search_product(product_name)
        
        if not results:
            return []
        
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
            
    except Exception as e:
        print(f"❌ Error processing {product_name}: {e}")
    
    return enhanced_matches

def run_bulk_fast():
    """Run enhanced workflow for all products with fast processing"""
    
    print("🚀 Fast Bulk Enhanced Product Matching Workflow")
    print("=" * 60)
    print("🎯 Preferred Retailers: Tesco → Ocado → Morrisons → Sainsbury's")
    print("⚡ Fast mode: Minimal output, reduced delays")
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
    print("⚡ Fast mode: 0.5s delay between products")
    print("💾 Progress saved every 5 products")
    
    # Ask user if they want to continue
    response = input(f"\nContinue with {len(remaining_products)} remaining products? (y/n): ").strip().lower()
    if response != 'y':
        print("❌ Cancelled by user")
        return
    
    successful_matches = 0
    failed_matches = 0
    start_time = time.time()
    
    # Process each remaining product
    for i, product_name in enumerate(remaining_products, 1):
        current_index = last_product_index + i
        
        # Show progress every 10 products
        if i % 10 == 0:
            elapsed = time.time() - start_time
            rate = i / elapsed if elapsed > 0 else 0
            eta = (len(remaining_products) - i) / rate if rate > 0 else 0
            print(f"📈 Progress: {i}/{len(remaining_products)} ({i/len(remaining_products)*100:.1f}%) - Rate: {rate:.1f} products/min - ETA: {eta/60:.1f} min")
        
        try:
            # Run enhanced workflow for this product
            matches = run_enhanced_workflow_fast(product_name)
            
            if matches:
                all_results.extend(matches)
                successful_matches += 1
                # Show only the best match
                best_match = matches[0]
                retailer = best_match['retailer']
                price = best_match['price']
                confidence = best_match['confidence']
                
                # Simple status indicator
                status = "✅" if confidence >= 0.7 else "🟡" if confidence >= 0.5 else "🔴"
                print(f"{status} {current_index:4d}/{len(product_names)}: {product_name[:40]:<40} | {retailer} £{price:.2f} ({confidence:.0%})")
            else:
                failed_matches += 1
                print(f"❌ {current_index:4d}/{len(product_names)}: {product_name[:40]:<40} | No matches")
            
            # Mark as completed
            completed_products.add(product_name)
            
            # Update progress every 5 products (faster than every product)
            if i % 5 == 0:
                progress["completed_products"] = list(completed_products)
                progress["results"] = all_results
                progress["last_product_index"] = current_index
                save_progress(progress)
            
            # Save results to CSV every 20 products
            if i % 20 == 0:
                try:
                    df_results = pd.DataFrame(all_results)
                    df_results.to_csv(RESULTS_FILE, index=False)
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
            if i % 5 == 0:
                progress["completed_products"] = list(completed_products)
                save_progress(progress)
        
        # Reduced delay between requests
        if i < len(remaining_products):
            time.sleep(0.5)  # Only 0.5 seconds instead of 2
    
    # Print final summary
    total_time = time.time() - start_time
    print(f"\n{'='*60}")
    print("📊 BULK PROCESSING SUMMARY")
    print(f"{'='*60}")
    print(f"Total Products: {len(product_names)}")
    print(f"Successfully Processed: {successful_matches}")
    print(f"Failed Matches: {failed_matches}")
    print(f"Success Rate: {(successful_matches/len(product_names)*100):.1f}%")
    print(f"Total Enhanced Matches Found: {len(all_results)}")
    print(f"Total Time: {total_time/60:.1f} minutes")
    print(f"Average Rate: {len(remaining_products)/(total_time/60):.1f} products/minute")
    
    # Save final results to CSV
    if all_results:
        try:
            df_results = pd.DataFrame(all_results)
            df_results.to_csv(RESULTS_FILE, index=False)
            print(f"\n💾 Final results saved to: {RESULTS_FILE}")
            
            # Show sample of results
            print(f"\n📋 Sample Results (first 3):")
            print(df_results.head(3).to_string(index=False))
            
        except Exception as e:
            print(f"❌ Error saving final results: {e}")
    
    # Clean up progress file
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)
        print(f"🧹 Progress file cleaned up")
    
    print(f"\n✅ Bulk processing completed!")

if __name__ == "__main__":
    run_bulk_fast()
