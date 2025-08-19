#!/usr/bin/env python3
"""
Enhanced Price Scraping Workflow
================================

High-accuracy price extraction from multiple sources with fallback strategies
"""

import pandas as pd
import argparse
import logging
from typing import Dict, List, Optional
from price_aggregator import PriceAggregator


class EnhancedPriceWorkflow:
    """Enhanced workflow with multi-source price aggregation"""
    
    def __init__(self, enable_tesco: bool = True, enable_morrisons: bool = False,
                 enable_ocado: bool = False, enable_amazon: bool = False,
                 clear_cache: bool = False):
        """Initialize enhanced workflow"""
        self.aggregator = PriceAggregator(
            enable_tesco=enable_tesco,
            enable_morrisons=enable_morrisons,
            enable_ocado=enable_ocado,
            enable_amazon=enable_amazon
        )
        
        if clear_cache:
            self.aggregator.clear_cache()
        
        # Enhanced similarity thresholds
        self.high_confidence_threshold = 0.7
        self.medium_confidence_threshold = 0.4
        self.low_confidence_threshold = 0.2
        
        print(f"🚀 Enhanced Price Workflow initialized with sources: {self.aggregator.enabled_sources}")
    
    def process_excel_file(self, input_file: str, output_file: str, max_products: int = None) -> None:
        """Process Excel file with enhanced accuracy - optimized for speed"""
        try:
            print(f"📊 Loading input file: {input_file}")
            df = pd.read_excel(input_file)
            
            if max_products:
                df = df.head(max_products)
            
            print(f"📋 Processing {len(df)} products with enhanced accuracy...")
            
            # Initialize results
            results = []
            stats = {
                'total': len(df),
                'found': 0,
                'high_confidence': 0,
                'medium_confidence': 0,
                'low_confidence': 0,
                'not_found': 0
            }
            
            # Process products in batches for better performance
            batch_size = 10
            for batch_start in range(0, len(df), batch_size):
                batch_end = min(batch_start + batch_size, len(df))
                batch_df = df.iloc[batch_start:batch_end]
                
                print(f"\n🔄 Processing batch {batch_start//batch_size + 1}/{(len(df)-1)//batch_size + 1} (products {batch_start+1}-{batch_end})")
                
                for index, row in batch_df.iterrows():
                    product_name = str(row.iloc[0])  # First column contains product names
                    
                    print(f"\n[{index + 1}/{len(df)}] Processing: {product_name}")
                    
                    # Get best prices from all sources
                    result = self.aggregator.get_best_prices(product_name)
                    
                    # Process result
                    processed_row = self._process_result(row, result, stats)
                    results.append(processed_row)
                    
                    # Progress update every 5 products
                    if (index + 1) % 5 == 0:
                        self._print_progress(stats, index + 1)
            
            # Create output DataFrame
            output_df = pd.DataFrame(results)
            
            # Save results
            output_df.to_excel(output_file, index=False)
            
            # Print final statistics
            self._print_final_stats(stats, output_file)
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Error processing file: {e}")
            raise
    
    def _process_result(self, original_row, result: Dict, stats: Dict) -> Dict:
        """Process individual result and update statistics"""
        processed_row = original_row.to_dict()
        
        if result['found']:
            stats['found'] += 1
            best_match = result['best_match']
            
            # Update confidence statistics
            confidence = result['confidence']
            if confidence >= self.high_confidence_threshold:
                stats['high_confidence'] += 1
                confidence_level = "HIGH"
            elif confidence >= self.medium_confidence_threshold:
                stats['medium_confidence'] += 1
                confidence_level = "MEDIUM"
            elif confidence >= self.low_confidence_threshold:
                stats['low_confidence'] += 1
                confidence_level = "LOW"
            else:
                stats['low_confidence'] += 1
                confidence_level = "VERY_LOW"
            
            # Add result data
            processed_row.update({
                'Found': 'Yes',
                'Confidence_Level': confidence_level,
                'Confidence_Score': f"{confidence:.3f}",
                'Best_Source': best_match['source'],
                'Matched_Product': best_match['name'],
                'Best_Price': best_match['price'],
                'Product_URL': best_match['url'],
                'Similarity_Score': f"{best_match['similarity']:.3f}"
            })
            
            # Add retailer breakdown
            if best_match['source'] == 'Trolley.co.uk':
                retailer_prices = best_match['retailer_prices']
                for retailer in ['Tesco', 'Morrisons', 'Ocado', 'Sainsbury\'s', 'ASDA', 'Wilko', 'Co-op']:
                    if retailer in retailer_prices:
                        price_data = retailer_prices[retailer]
                        if isinstance(price_data, dict) and 'price' in price_data:
                            processed_row[f'{retailer}_Price'] = price_data['price']
                        else:
                            processed_row[f'{retailer}_Price'] = 0
                    else:
                        processed_row[f'{retailer}_Price'] = 0
            
            elif best_match['source'] == 'Tesco.com':
                processed_row['Tesco_Price'] = best_match['price']
                for retailer in ['Morrisons', 'Ocado', 'Sainsbury\'s', 'ASDA', 'Wilko', 'Co-op']:
                    processed_row[f'{retailer}_Price'] = 0
            
            print(f"✅ Found: {best_match['name']} (Confidence: {confidence:.3f})")
            
        else:
            stats['not_found'] += 1
            processed_row.update({
                'Found': 'No',
                'Confidence_Level': 'NOT_FOUND',
                'Confidence_Score': '0.000',
                'Best_Source': 'None',
                'Matched_Product': 'None',
                'Best_Price': 0,
                'Product_URL': 'None',
                'Similarity_Score': '0.000'
            })
            
            # Set all retailer prices to 0
            for retailer in ['Tesco', 'Morrisons', 'Ocado', 'Sainsbury\'s', 'ASDA', 'Wilko', 'Co-op']:
                processed_row[f'{retailer}_Price'] = 0
            
            print(f"❌ Not found")
        
        return processed_row
    
    def _print_progress(self, stats: Dict, current: int) -> None:
        """Print progress update"""
        found_rate = (stats['found'] / current) * 100
        print(f"\n📊 Progress: {current}/{stats['total']} | Found: {stats['found']} ({found_rate:.1f}%)")
    
    def _print_final_stats(self, stats: Dict, output_file: str) -> None:
        """Print final statistics"""
        print(f"\n🎯 FINAL RESULTS")
        print(f"=" * 50)
        print(f"Total Products: {stats['total']}")
        print(f"Found: {stats['found']} ({(stats['found']/stats['total'])*100:.1f}%)")
        print(f"  - High Confidence: {stats['high_confidence']}")
        print(f"  - Medium Confidence: {stats['medium_confidence']}")
        print(f"  - Low Confidence: {stats['low_confidence']}")
        print(f"Not Found: {stats['not_found']}")
        print(f"Output saved to: {output_file}")
        print(f"=" * 50)


def main():
    """Main function with enhanced command line options"""
    parser = argparse.ArgumentParser(description='Enhanced Price Scraping Workflow')
    parser.add_argument('input_file', help='Input Excel file path')
    parser.add_argument('--output', '-o', default=None, help='Output Excel file path')
    parser.add_argument('--max-products', '-m', type=int, default=None, help='Maximum number of products to process')
    parser.add_argument('--clear-cache', action='store_true', help='Clear cache before processing')
    parser.add_argument('--enable-tesco', action='store_true', default=True, help='Enable Tesco.com scraping')
    parser.add_argument('--enable-morrisons', action='store_true', help='Enable Morrisons.com scraping')
    parser.add_argument('--enable-ocado', action='store_true', help='Enable Ocado.com scraping')
    parser.add_argument('--enable-amazon', action='store_true', help='Enable Amazon.co.uk scraping')
    
    args = parser.parse_args()
    
    # Generate output filename if not provided
    if not args.output:
        input_name = args.input_file.replace('.xlsx', '').replace('.xls', '')
        args.output = f"{input_name}_enhanced_results.xlsx"
    
    # Initialize and run workflow
    workflow = EnhancedPriceWorkflow(
        enable_tesco=args.enable_tesco,
        enable_morrisons=args.enable_morrisons,
        enable_ocado=args.enable_ocado,
        enable_amazon=args.enable_amazon,
        clear_cache=args.clear_cache
    )
    
    workflow.process_excel_file(args.input_file, args.output, args.max_products)


if __name__ == "__main__":
    main()
