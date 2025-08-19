#!/usr/bin/env python3
"""
Price Aggregator
================

Combines and ranks price data from multiple sources for maximum accuracy
"""

import logging
from typing import Dict, List, Optional
from trolley_scraper_fixed import FixedTrolleyScraper
from tesco_scraper import TescoScraper


class PriceAggregator:
    """Aggregates price data from multiple sources"""
    
    def __init__(self, enable_tesco: bool = True, enable_morrisons: bool = False, 
                 enable_ocado: bool = False, enable_amazon: bool = False):
        """Initialize price aggregator with enabled sources"""
        self.trolley_scraper = FixedTrolleyScraper()
        self.tesco_scraper = TescoScraper() if enable_tesco else None
        self.morrisons_scraper = None  # TODO: Implement
        self.ocado_scraper = None      # TODO: Implement
        self.amazon_scraper = None     # TODO: Implement
        
        self.enabled_sources = ['Trolley']
        if enable_tesco:
            self.enabled_sources.append('Tesco')
        if enable_morrisons:
            self.enabled_sources.append('Morrisons')
        if enable_ocado:
            self.enabled_sources.append('Ocado')
        if enable_amazon:
            self.enabled_sources.append('Amazon')
    
    def get_best_prices(self, product_name: str) -> Dict:
        """Get best price data from all enabled sources - optimized for speed"""
        print(f"\n🔍 AGGREGATOR: Searching for '{product_name}' across {len(self.enabled_sources)} sources")
        
        all_results = []
        
        # 1. Trolley.co.uk (primary source)
        print(f"📊 Source 1/2: Trolley.co.uk")
        trolley_results = self.trolley_scraper.search_with_fallback(product_name)
        if trolley_results:
            # Get the best Trolley result
            best_trolley = max(trolley_results, key=lambda x: x['confidence_score'])
            all_results.append({
                'source': 'Trolley.co.uk',
                'name': best_trolley['name'],
                'price': self._extract_best_price(best_trolley['retailer_prices']),
                'url': best_trolley['url'],
                'confidence': best_trolley['confidence_score'],
                'similarity': best_trolley['similarity_score'],
                'retailer_prices': best_trolley['retailer_prices']
            })
            
            # Early exit if we found a high-confidence match from Trolley
            if best_trolley['confidence_score'] > 0.8:
                print(f"✅ AGGREGATOR: High-confidence match from Trolley, skipping Tesco")
                return {
                    'product_name': product_name,
                    'best_match': all_results[0],
                    'all_matches': all_results,
                    'found': True,
                    'confidence': best_trolley['confidence_score']
                }
        
        # 2. Tesco (direct source) - only if Trolley didn't find good results
        if self.tesco_scraper and (not all_results or all_results[0]['confidence'] < 0.6):
            print(f"📊 Source 2/2: Tesco.com")
            tesco_result = self.tesco_scraper.search_product(product_name)
            if tesco_result and tesco_result['similarity_score'] >= 0.15:
                all_results.append({
                    'source': 'Tesco.com',
                    'name': tesco_result['name'],
                    'price': tesco_result['price'],
                    'url': tesco_result['url'],
                    'confidence': tesco_result['similarity_score'] * 0.8,  # Scale to confidence
                    'similarity': tesco_result['similarity_score'],
                    'retailer_prices': {'Tesco': {'price': tesco_result['price']}} if tesco_result['price'] else {}
                })
        
        # Rank results by confidence
        all_results.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Return best result
        if all_results:
            best_result = all_results[0]
            print(f"✅ AGGREGATOR: Best match from {best_result['source']} (confidence: {best_result['confidence']:.3f})")
            
            return {
                'product_name': product_name,
                'best_match': best_result,
                'all_matches': all_results,
                'found': True,
                'confidence': best_result['confidence']
            }
        else:
            print(f"❌ AGGREGATOR: No matches found across all sources")
            return {
                'product_name': product_name,
                'best_match': None,
                'all_matches': [],
                'found': False,
                'confidence': 0.0
            }
    
    def _extract_best_price(self, retailer_prices: Dict) -> Optional[float]:
        """Extract the best price from retailer prices (Tesco first, then others)"""
        if not retailer_prices:
            return None
        
        # Priority order: Tesco, Morrisons, Ocado, Sainsbury's, ASDA, Wilko, Co-op
        priority_retailers = ['Tesco', 'Morrisons', 'Ocado', 'Sainsbury\'s', 'ASDA', 'Wilko', 'Co-op']
        
        for retailer in priority_retailers:
            if retailer in retailer_prices:
                price_data = retailer_prices[retailer]
                if isinstance(price_data, dict) and 'price' in price_data:
                    return price_data['price']
                elif isinstance(price_data, (int, float)):
                    return float(price_data)
        
        # If no priority retailer found, return first available price
        for retailer, price_data in retailer_prices.items():
            if isinstance(price_data, dict) and 'price' in price_data:
                return price_data['price']
            elif isinstance(price_data, (int, float)):
                return float(price_data)
        
        return None
    
    def get_retailer_breakdown(self, product_name: str) -> Dict:
        """Get detailed breakdown of prices from each retailer"""
        result = self.get_best_prices(product_name)
        
        if not result['found']:
            return result
        
        # Extract individual retailer prices
        retailer_breakdown = {}
        
        if result['best_match']['source'] == 'Trolley.co.uk':
            trolley_prices = result['best_match']['retailer_prices']
            for retailer, price_data in trolley_prices.items():
                if isinstance(price_data, dict) and 'price' in price_data:
                    retailer_breakdown[retailer] = price_data['price']
        
        elif result['best_match']['source'] == 'Tesco.com':
            if result['best_match']['price']:
                retailer_breakdown['Tesco'] = result['best_match']['price']
        
        result['retailer_breakdown'] = retailer_breakdown
        return result
    
    def clear_cache(self):
        """Clear cache from all scrapers"""
        self.trolley_scraper.clear_cache()
        print("🗑️ Cleared cache from all scrapers")
