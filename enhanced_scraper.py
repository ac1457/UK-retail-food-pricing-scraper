#!/usr/bin/env python3
"""
Enhanced Scraper with Advanced Product Matching
===============================================

Integrates the enhanced product matching system with the existing trolley scraper
for improved accuracy and validation.
"""

import asyncio
import logging
from typing import List, Dict, Optional
from trolley_scraper_fixed import FixedTrolleyScraper
from enhanced_matcher import EnhancedProductMatcher, ProductMatch, parse_retailer_product
from cache_manager import CacheManager


class EnhancedScraper:
    """Enhanced scraper with advanced product matching and validation"""
    
    def __init__(self, cache_duration_hours: int = 24):
        """Initialize the enhanced scraper"""
        self.trolley_scraper = FixedTrolleyScraper(cache_duration_hours=cache_duration_hours)
        self.matcher = EnhancedProductMatcher()
        self.cache_manager = CacheManager(cache_duration_hours=cache_duration_hours)
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    async def enhanced_scrape_product_prices(self, product_name: str, 
                                           retailer_urls: Optional[Dict[str, str]] = None) -> List[Dict]:
        """
        Enhanced scraping with multiple validation steps
        
        Args:
            product_name: The product name to search for
            retailer_urls: Optional dict of retailer URLs to scrape directly
            
        Returns:
            List of dictionaries with enhanced product matches and validation
        """
        results = []
        
        try:
            # Step 1: Use Trolley scraper for initial results
            print(f"🔍 Enhanced search for: {product_name}")
            trolley_results = self.trolley_scraper.search_product(product_name)
            
            if trolley_results:
                # Step 2: Apply enhanced matching to trolley results
                enhanced_matches = self._apply_enhanced_matching(product_name, trolley_results)
                results.extend(enhanced_matches)
            
            # Step 3: If we have specific retailer URLs, scrape them directly
            if retailer_urls:
                direct_results = await self._scrape_direct_retailers(product_name, retailer_urls)
                results.extend(direct_results)
            
            # Step 4: Sort by confidence and remove duplicates
            final_results = self._sort_and_deduplicate(results)
            
            print(f"✅ Enhanced search completed: {len(final_results)} high-confidence matches")
            return final_results
            
        except Exception as e:
            self.logger.error(f"Error in enhanced scraping: {e}")
            return []
    
    def _apply_enhanced_matching(self, product_name: str, trolley_results: List[Dict]) -> List[Dict]:
        """Apply enhanced matching to trolley results"""
        enhanced_results = []
        
        for result in trolley_results:
            # Extract retailer prices from the result
            retailer_prices = result.get('retailer_prices', {})
            
            for retailer, price_data in retailer_prices.items():
                if not price_data or not isinstance(price_data, dict):
                    continue
                
                # Create item dict for matching
                item = {
                    'name': result.get('name', ''),
                    'price': price_data.get('price'),
                    'price_text': price_data.get('price_text', ''),
                    'retailer': retailer,
                    'url': result.get('url')
                }
                
                # Apply enhanced matching
                match = self.matcher.enhanced_product_match(product_name, [item])
                
                if match:
                    enhanced_results.append({
                        'retailer': retailer,
                        'product': match.name,
                        'price': match.price,
                        'unit_price': match.unit_price,
                        'weight': match.weight,
                        'confidence': match.confidence,
                        'match_type': match.match_type,
                        'validation_issues': match.validation_issues,
                        'url': match.url,
                        'source': 'trolley_enhanced'
                    })
        
        return enhanced_results
    
    async def _scrape_direct_retailers(self, product_name: str, 
                                     retailer_urls: Dict[str, str]) -> List[Dict]:
        """Scrape specific retailers directly"""
        results = []
        
        for retailer, url in retailer_urls.items():
            try:
                print(f"🔍 Direct scraping {retailer}: {url}")
                
                # This would integrate with individual retailer scrapers
                # For now, we'll use a placeholder
                scraped_items = await self._scrape_retailer(retailer, url)
                
                if scraped_items:
                    # Apply enhanced matching
                    match = self.matcher.enhanced_product_match(product_name, scraped_items)
                    
                    if match:
                        results.append({
                            'retailer': retailer,
                            'product': match.name,
                            'price': match.price,
                            'unit_price': match.unit_price,
                            'weight': match.weight,
                            'confidence': match.confidence,
                            'match_type': match.match_type,
                            'validation_issues': match.validation_issues,
                            'url': match.url,
                            'source': 'direct_scraping'
                        })
                
            except Exception as e:
                self.logger.error(f"Error scraping {retailer}: {e}")
        
        return results
    
    async def _scrape_retailer(self, retailer: str, url: str) -> List[Dict]:
        """Scrape a specific retailer (placeholder for now)"""
        # This would integrate with individual retailer scrapers
        # For now, return empty list
        return []
    
    def _sort_and_deduplicate(self, results: List[Dict]) -> List[Dict]:
        """Sort results by confidence and remove duplicates"""
        if not results:
            return []
        
        # Remove duplicates based on retailer and product name
        seen = set()
        unique_results = []
        
        for result in results:
            key = (result['retailer'].lower(), result['product'].lower())
            if key not in seen:
                seen.add(key)
                unique_results.append(result)
        
        # Sort by confidence (highest first)
        unique_results.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        return unique_results
    
    def validate_all_results(self, results: List[Dict]) -> Dict:
        """Validate all results and provide summary"""
        validation_summary = {
            'total_results': len(results),
            'high_confidence': 0,
            'medium_confidence': 0,
            'low_confidence': 0,
            'validation_issues': [],
            'price_range_violations': 0,
            'unit_price_mismatches': 0
        }
        
        for result in results:
            confidence = result.get('confidence', 0)
            
            if confidence >= 0.8:
                validation_summary['high_confidence'] += 1
            elif confidence >= 0.6:
                validation_summary['medium_confidence'] += 1
            else:
                validation_summary['low_confidence'] += 1
            
            # Check validation issues
            issues = result.get('validation_issues', [])
            validation_summary['validation_issues'].extend(issues)
            
            for issue in issues:
                if 'outside expected range' in issue:
                    validation_summary['price_range_violations'] += 1
                elif 'doesn\'t match calculated value' in issue:
                    validation_summary['unit_price_mismatches'] += 1
        
        return validation_summary
    
    def print_enhanced_results(self, results: List[Dict]):
        """Print enhanced results with validation information"""
        if not results:
            print("❌ No results found")
            return
        
        print(f"\n🎯 ENHANCED SEARCH RESULTS")
        print("=" * 60)
        
        for i, result in enumerate(results, 1):
            confidence = result.get('confidence', 0)
            confidence_emoji = "🟢" if confidence >= 0.8 else "🟡" if confidence >= 0.6 else "🔴"
            
            print(f"\n{i}. {confidence_emoji} {result['retailer']}")
            print(f"   Product: {result['product']}")
            print(f"   Price: £{result.get('price', 'N/A'):.2f}")
            
            if result.get('unit_price'):
                print(f"   Unit Price: £{result['unit_price']:.2f}")
            
            if result.get('weight'):
                print(f"   Weight: {result['weight']}")
            
            print(f"   Confidence: {confidence:.2%} ({result.get('match_type', 'unknown')})")
            
            # Show validation issues if any
            issues = result.get('validation_issues', [])
            if issues:
                print(f"   ⚠️  Validation Issues:")
                for issue in issues:
                    print(f"      - {issue}")
        
        # Print validation summary
        validation_summary = self.validate_all_results(results)
        print(f"\n📊 VALIDATION SUMMARY")
        print("=" * 30)
        print(f"Total Results: {validation_summary['total_results']}")
        print(f"High Confidence: {validation_summary['high_confidence']}")
        print(f"Medium Confidence: {validation_summary['medium_confidence']}")
        print(f"Low Confidence: {validation_summary['low_confidence']}")
        print(f"Price Range Violations: {validation_summary['price_range_violations']}")
        print(f"Unit Price Mismatches: {validation_summary['unit_price_mismatches']}")


# Example usage and testing
async def test_enhanced_scraper():
    """Test the enhanced scraper with sample products"""
    scraper = EnhancedScraper()
    
    # Test products
    test_products = [
        "Heinz Baked Beans 415g",
        "Branston Baked Beans 410g",
        "Tesco Baked Beans 420g",
        "Heinz Cream of Tomato Soup 400g"
    ]
    
    for product in test_products:
        print(f"\n🧪 Testing Enhanced Scraper: {product}")
        print("-" * 50)
        
        results = await scraper.enhanced_scrape_product_prices(product)
        scraper.print_enhanced_results(results)
        
        # Add delay between tests
        await asyncio.sleep(2)


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_enhanced_scraper())
