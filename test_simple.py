#!/usr/bin/env python3
"""
Simple test to debug the issue
"""

import pandas as pd
from trolley_scraper_fixed import FixedTrolleyScraper

def test_simple():
    """Simple test"""
    print("🧪 Simple test")
    print("=" * 30)
    
    # Test reading Excel file
    try:
        df = pd.read_excel("Pricing Exp_final_fixed.xlsx")
        print(f"✅ Excel file read successfully")
        print(f"   Columns: {list(df.columns)}")
        print(f"   Rows: {len(df)}")
        
        # Test first product
        if len(df) > 0:
            first_product = df.iloc[0]['Product_Name']
            print(f"   First product: {first_product}")
            
            # Test scraper
            scraper = FixedTrolleyScraper()
            scraper.clear_cache()
            
            print(f"🔍 Testing scraper with: {first_product}")
            results = scraper.search_product(first_product)
            
            if results:
                print(f"✅ Found {len(results)} results")
                best = max(results, key=lambda x: x['similarity_score'])
                print(f"   Best match: {best['name']} (Score: {best['similarity_score']:.3f})")
            else:
                print(f"❌ No results found")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple()
