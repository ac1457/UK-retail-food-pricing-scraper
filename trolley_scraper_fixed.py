#!/usr/bin/env python3
"""
Fixed Trolley.co.uk Scraper
==========================

A completely fixed version that addresses:
1. Too strict similarity matching
2. Broken price extraction
3. Poor search optimization
4. Corrupted competitor names
"""

import pandas as pd
import re
import logging
import time
import random
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup
from curl_cffi import Session
import urllib.parse

from constants import REQUEST_HEADER
from filemanager import Config
from cache_manager import CacheManager


class FixedTrolleyScraper:
    """Fixed scraper for Trolley.co.uk price comparison website"""
    
    def __init__(self, browser_profile: str = "chrome120", cache_duration_hours: int = 24):
        """Initialize with browser profile for impersonation"""
        self.browser_profile = browser_profile
        self.session = Session()
        self.session.headers.update(REQUEST_HEADER)
        self.request_delay = Config.get_request_delay()
        
        # Set initial browser profile
        self._set_browser_profile(browser_profile)
        
        # Target retailers we want to extract prices from (in preference order)
        self.target_retailers = ['Tesco', 'Morrisons', 'Ocado', 'Sainsbury\'s', 'ASDA', 'Wilko', 'Co-op']
        
        # Initialize cache manager
        self.cache_manager = CacheManager(cache_duration_hours=cache_duration_hours)
    
    def _set_browser_profile(self, profile: str):
        """Set the browser profile for impersonation"""
        try:
            self.session.impersonate = profile
            logging.getLogger(__name__).info(f"Set browser profile: {profile}")
        except Exception as e:
            logging.getLogger(__name__).warning(f"Failed to set browser profile {profile}: {e}")
            # Fallback to default
            self.session.impersonate = "chrome120"
    
    def _smart_delay(self):
        """Add intelligent delays to mimic human behavior - optimized for speed"""
        # Faster delays: 0.5-1.5 seconds instead of 1-2 seconds
        delay = random.uniform(0.5, 1.5)
        time.sleep(delay)
        
        # Reduced chance of longer delays (2% instead of 5%)
        if random.random() < 0.02:
            long_delay = random.uniform(2.0, 4.0)  # Reduced from 3-6 seconds
            logging.getLogger(__name__).info(f"Adding longer delay: {long_delay:.1f}s")
            time.sleep(long_delay)
    
    def search_product(self, product_name: str) -> List[Dict]:
        """
        Search for a product on Trolley.co.uk and return results with prices from multiple retailers
        
        Args:
            product_name: The product name to search for
            
        Returns:
            List of dictionaries containing product info and prices from different retailers
        """
        try:
            # Check cache first
            cached_results = self.cache_manager.get_search_results(product_name)
            if cached_results:
                print(f"📋 Returning {len(cached_results)} cached results for: {product_name}")
                return cached_results
            
            # Clean the search term with multiple strategies
            search_terms = self._generate_search_terms(product_name)
            
            all_results = []
            
            for search_term in search_terms:
                # Trolley search URL
                search_url = f"https://www.trolley.co.uk/search?q={search_term}"
                
                print(f"🔍 Searching Trolley.co.uk: {search_url}")
                
                # Add random user agent
                user_agents = [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15"
                ]
                
                headers = self.session.headers.copy()
                headers['User-Agent'] = random.choice(user_agents)
                
                response = self.session.get(search_url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract product cards
                    product_cards = self._extract_product_cards(soup)
                    print(f"      Found {len(product_cards)} potential product cards")
                    
                    # Process each card
                    for i, card in enumerate(product_cards[:5], 1):  # Reduced to first 5 cards for speed
                        print(f"        Checking card {i}: {card.get_text()[:50]}...")
                        
                        result = self._extract_product_info(card, product_name)
                        if result:
                            print(f"        ✅ Found match: {result['name']} (score: {result['similarity_score']:.3f})")
                            all_results.append(result)
                        else:
                            print(f"        ❌ No match found for this card")
                    
                    # Stop early if we found a very good match (similarity > 0.8)
                    if all_results and max(r['similarity_score'] for r in all_results) > 0.8:
                        print(f"      ✅ Found excellent match, stopping search")
                        break
                    
                    # Continue searching through all terms to find the best possible match
                    print(f"      Continuing to next search term for better matches")
                    
                    # Smart delay between search attempts
                    self._smart_delay()
                else:
                    print(f"      ❌ Search failed: HTTP {response.status_code}")
            
            # Sort results by similarity score (highest first)
            all_results.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            # Cache the results
            self.cache_manager.set_search_results(product_name, all_results)
            
            return all_results
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Error searching product: {e}")
            return []
    
    def search_with_fallback(self, product_name: str) -> List[Dict]:
        """Enhanced search with multiple fallback strategies for maximum accuracy"""
        try:
            # Check cache first
            cached_results = self.cache_manager.get_search_results(product_name)
            if cached_results:
                print(f"📋 Returning {len(cached_results)} cached results for: {product_name}")
                return cached_results
            
            all_results = []
            
            # Strategy 1: Standard search with current thresholds
            print(f"🔍 Strategy 1: Standard search for: {product_name}")
            results = self._search_with_threshold(product_name, min_similarity=0.12)
            all_results.extend(results)
            
            # Early exit if we found excellent matches
            if all_results and max(r['similarity_score'] for r in all_results) > 0.85:
                print(f"✅ Found excellent match, skipping additional strategies")
                unique_results = self._remove_duplicates(all_results)
                unique_results.sort(key=lambda x: x['confidence_score'], reverse=True)
                self.cache_manager.set_search_results(product_name, unique_results)
                return unique_results
            
            # Strategy 2: If no good results, try with lower threshold
            if not all_results or max(r['similarity_score'] for r in all_results) < 0.25:
                print(f"🔍 Strategy 2: Lower threshold search for: {product_name}")
                results = self._search_with_threshold(product_name, min_similarity=0.08)
                all_results.extend(results)
                
                # Early exit if we found good matches
                if all_results and max(r['similarity_score'] for r in all_results) > 0.70:
                    print(f"✅ Found good match, skipping additional strategies")
                    unique_results = self._remove_duplicates(all_results)
                    unique_results.sort(key=lambda x: x['confidence_score'], reverse=True)
                    self.cache_manager.set_search_results(product_name, unique_results)
                    return unique_results
            
            # Strategy 3: If still no results, try simplified search terms
            if not all_results or max(r['similarity_score'] for r in all_results) < 0.20:
                print(f"🔍 Strategy 3: Simplified search terms for: {product_name}")
                results = self._search_with_simplified_terms(product_name)
                all_results.extend(results)
            
            # Strategy 4: Brand-only search as last resort
            if not all_results:
                print(f"🔍 Strategy 4: Brand-only search for: {product_name}")
                results = self._search_brand_only(product_name)
                all_results.extend(results)
            
            # Remove duplicates and sort by confidence
            unique_results = self._remove_duplicates(all_results)
            unique_results.sort(key=lambda x: x['confidence_score'], reverse=True)
            
            # Cache the results
            self.cache_manager.set_search_results(product_name, unique_results)
            
            return unique_results
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Error in fallback search: {e}")
            return []
    
    def _search_with_threshold(self, product_name: str, min_similarity: float) -> List[Dict]:
        """Search with specific similarity threshold - optimized for speed"""
        search_terms = self._generate_search_terms(product_name)
        all_results = []
        
        for search_term in search_terms:
            search_url = f"https://www.trolley.co.uk/search?q={search_term}"
            print(f"      Searching: {search_url}")
            
            headers = self.session.headers.copy()
            headers['User-Agent'] = random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0"
            ])
            
            response = self.session.get(search_url, headers=headers, timeout=20)  # Reduced timeout
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                product_cards = self._extract_product_cards(soup)
                
                # Process fewer cards for speed, but check more if needed
                cards_to_check = 6 if min_similarity >= 0.12 else 8
                
                for i, card in enumerate(product_cards[:cards_to_check], 1):
                    result = self._extract_product_info_with_confidence(card, product_name, min_similarity)
                    if result:
                        all_results.append(result)
                        # Early exit if we found a very good match
                        if result['similarity_score'] > 0.85:
                            print(f"      ✅ Found excellent match, stopping search")
                            return all_results
                
                # Early stopping for excellent matches
                if all_results and max(r['similarity_score'] for r in all_results) > 0.85:
                    break
                
                # Faster delays for speed
                time.sleep(random.uniform(0.5, 1.0))  # Reduced delay
        
        return all_results
    
    def _search_with_simplified_terms(self, product_name: str) -> List[Dict]:
        """Search with simplified, broader search terms"""
        brand, product = self._extract_brand_and_product(product_name)
        
        simplified_terms = []
        if brand:
            simplified_terms.append(brand)
            if product:
                # Try brand + first few words of product
                product_words = product.split()[:3]  # First 3 words
                simplified_terms.append(f"{brand} {' '.join(product_words)}")
        
        all_results = []
        for term in simplified_terms:
            results = self._search_with_threshold(term, min_similarity=0.06)
            all_results.extend(results)
        
        return all_results
    
    def _search_brand_only(self, product_name: str) -> List[Dict]:
        """Search using only the brand name"""
        brand, _ = self._extract_brand_and_product(product_name)
        if not brand:
            return []
        
        return self._search_with_threshold(brand, min_similarity=0.05)
    
    def _extract_product_info_with_confidence(self, card, original_product_name: str, min_similarity: float) -> Optional[Dict]:
        """Extract product info with enhanced confidence scoring"""
        try:
            product_name = self._extract_product_name_from_card(card)
            
            if not product_name or len(product_name) < 3:
                return None
            
            # Calculate similarity
            similarity_score = self._calculate_similarity_improved(product_name, original_product_name)
            
            if similarity_score < min_similarity:
                return None
            
            # Extract other info
            product_url = self._extract_product_url(card)
            quantity = self._extract_quantity(product_name)
            brand = self._extract_brand(product_name)
            
            # Get retailer prices
            retailer_prices = {}
            if product_url:
                retailer_prices = self._get_retailer_prices_fixed(product_url)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                similarity_score, product_name, original_product_name, retailer_prices
            )
            
            return {
                'name': product_name,
                'url': product_url,
                'brand': brand,
                'quantity': quantity,
                'similarity_score': similarity_score,
                'confidence_score': confidence_score,
                'retailer_prices': retailer_prices,
                'website': 'Trolley.co.uk',
                'original_search': original_product_name,
                'search_strategy': 'fallback'
            }
            
        except Exception as e:
            logging.getLogger(__name__).warning(f"Error extracting product info: {e}")
            return None
    
    def _calculate_confidence_score(self, similarity_score: float, product_name: str, 
                                  original_product_name: str, retailer_prices: Dict) -> float:
        """Calculate confidence score based on multiple factors"""
        confidence = similarity_score * 0.6  # Base confidence from similarity
        
        # Bonus for having retailer prices
        if retailer_prices:
            confidence += 0.2
        
        # Bonus for exact brand match
        original_brand, _ = self._extract_brand_and_product(original_product_name)
        found_brand, _ = self._extract_brand_and_product(product_name)
        if original_brand and found_brand and self._are_brands_similar(original_brand, found_brand):
            confidence += 0.15
        
        # Bonus for quantity match
        original_quantity = self._extract_quantity(original_product_name)
        found_quantity = self._extract_quantity(product_name)
        if original_quantity and found_quantity and original_quantity == found_quantity:
            confidence += 0.05
        
        return min(1.0, confidence)
    
    def _remove_duplicates(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results based on URL and name"""
        seen_urls = set()
        seen_names = set()
        unique_results = []
        
        for result in results:
            url = result.get('url', '')
            name = result.get('name', '').lower()
            
            if url not in seen_urls and name not in seen_names:
                seen_urls.add(url)
                seen_names.add(name)
                unique_results.append(result)
        
        return unique_results
    
    def _generate_search_terms(self, product_name: str) -> List[str]:
        """Generate multiple search terms for better results - optimized for speed"""
        search_terms = []
        
        # Extract brand and product
        brand, product = self._extract_brand_and_product(product_name)
        
        # For multipack products, prioritize "Family Pack" search terms
        if self._is_multipack(product_name):
            multipack_terms = self._generate_multipack_terms(product_name, brand)
            # Prioritize more specific terms first
            specific_terms = [term for term in multipack_terms if "Baked Beans" in term or "Family Pack" in term]
            general_terms = [term for term in multipack_terms if term not in specific_terms]
            search_terms.extend(specific_terms + general_terms)
        
        # Strategy 1: Full product name
        full_term = self._clean_search_term(product_name)
        search_terms.append(full_term)
        
        # Strategy 2: Brand + product (if we have both)
        if brand and product:
            brand_product_term = self._clean_search_term(f"{brand} {product}")
            if brand_product_term != full_term:
                search_terms.append(brand_product_term)
        
        # Strategy 3: Just the product name (without brand)
        if product and product != product_name:
            product_only_term = self._clean_search_term(product)
            search_terms.append(product_only_term)
        
        # Strategy 4: Brand only (for products that might be found by brand)
        if brand:
            brand_only_term = self._clean_search_term(brand)
            search_terms.append(brand_only_term)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_terms = []
        for term in search_terms:
            if term not in seen:
                seen.add(term)
                unique_terms.append(term)
        
        return unique_terms[:2]  # Reduced from 3 to 2 search strategies for speed
    
    def _clean_search_term(self, product_name: str) -> str:
        """Clean product name for search"""
        import re
        
        # Remove special characters but keep spaces and hyphens
        clean_name = re.sub(r'[^\w\s-]', ' ', product_name)
        
        # Normalize multiple spaces
        clean_name = re.sub(r'\s+', ' ', clean_name)
        
        # Trim whitespace
        clean_name = clean_name.strip()
        
        # URL encode the search term
        return urllib.parse.quote(clean_name)
    
    def _extract_product_cards(self, soup: BeautifulSoup) -> List:
        """Extract product cards from search results page"""
        # Look for product cards in various possible containers
        cards = []
        
        # Common selectors for product cards
        selectors = [
            '[data-testid="product-card"]',
            '.product-card',
            '.search-result',
            '.product-item',
            'article',
            '.card',
            '[class*="product"]',
            '[class*="search"]'
        ]
        
        for selector in selectors:
            found_cards = soup.select(selector)
            if found_cards:
                cards.extend(found_cards)
                break
        
        # If no cards found with selectors, look for any div with product-like content
        if not cards:
            all_divs = soup.find_all('div')
            for div in all_divs:
                text = div.get_text().strip()
                # Check if this div contains product-like information
                if (len(text) > 20 and len(text) < 500 and 
                    ('£' in text or 'g' in text or 'ml' in text or 'kg' in text) and
                    not any(word in text.lower() for word in ['cookie', 'privacy', 'terms', 'help', 'contact'])):
                    cards.append(div)
        
        return cards
    
    def _extract_product_info(self, card, original_product_name: str) -> Optional[Dict]:
        """Extract product information from a card with improved matching"""
        try:
            # Extract product name from card
            product_name = self._extract_product_name_from_card(card)
            
            if not product_name or len(product_name) < 3:
                return None
            
            # Calculate similarity with MUCH LOWER threshold
            similarity_score = self._calculate_similarity_improved(product_name, original_product_name)
            
            # More lenient threshold for better matching
            if similarity_score < 0.12:  # Reduced from 0.15 to 0.12 for better matching
                return None
            
            # Extract product URL
            product_url = self._extract_product_url(card)
            
            # Extract quantity and brand
            quantity = self._extract_quantity(product_name)
            brand = self._extract_brand(product_name)
            
            # Get detailed product info if we have a URL
            retailer_prices = {}
            if product_url:
                retailer_prices = self._get_retailer_prices_fixed(product_url)
            
            return {
                'name': product_name,
                'url': product_url,
                'brand': brand,
                'quantity': quantity,
                'similarity_score': similarity_score,
                'retailer_prices': retailer_prices,
                'website': 'Trolley.co.uk',
                'original_search': original_product_name
            }
            
        except Exception as e:
            logging.getLogger(__name__).warning(f"Error extracting product info: {e}")
            return None
    
    def _extract_product_name_from_card(self, card) -> str:
        """Extract product name from card with multiple strategies"""
        # Strategy 1: Look for heading elements
        for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            heading = card.find(tag)
            if heading:
                name = heading.get_text().strip()
                if name and len(name) > 3:
                    return self._clean_extracted_name(name)
        
        # Strategy 1.5: Look for product name in text that contains "Family Pack"
        all_text = card.get_text()
        if "Family Pack" in all_text:
            # Extract text around "Family Pack"
            lines = all_text.split('\n')
            for line in lines:
                if "Family Pack" in line:
                    return self._clean_extracted_name(line)
        
        # Strategy 1.6: Look for "Baked Beans" in the text
        if "Baked Beans" in all_text:
            lines = all_text.split('\n')
            for line in lines:
                if "Baked Beans" in line and "Heinz" in line:
                    return self._clean_extracted_name(line)
        
        # Strategy 1.7: Look for concatenated text like "415g6HeinzBaked Beans"
        if "Heinz" in all_text and "Baked" in all_text and "Beans" in all_text:
            # Find the line containing Heinz and Baked Beans
            lines = all_text.split('\n')
            for line in lines:
                if "Heinz" in line and "Baked" in line and "Beans" in line:
                    # Clean up concatenated text
                    cleaned_line = line.replace('6Heinz', '6 Heinz ').replace('BakedBeans', 'Baked Beans')
                    return self._clean_extracted_name(cleaned_line)
        
        # Strategy 2: Look for link text
        link = card.find('a')
        if link:
            name = link.get_text().strip()
            if name and len(name) > 3:
                return self._clean_extracted_name(name)
        
        # Strategy 3: Look for any text that looks like a product name
        all_text = card.get_text().strip()
        lines = [line.strip() for line in all_text.split('\n') if line.strip()]
        
        for line in lines:
            # Skip lines that are too short or too long
            if len(line) < 5 or len(line) > 200:
                continue
            
            # Skip lines that contain navigation/UI text
            if any(word in line.lower() for word in ['cookie', 'privacy', 'terms', 'help', 'contact', 'add to', 'buy', 'shop']):
                continue
            
            # Skip lines that are just prices
            if re.match(r'^[£€$]?\d+\.?\d*$', line.strip()):
                continue
            
            return self._clean_extracted_name(line)
        
        return ""
    
    def _clean_extracted_name(self, name: str) -> str:
        """Clean extracted product name by separating concatenated components"""
        import re
        
        # Remove price information (anything with £ and numbers)
        name = re.sub(r'£\s*\d+\.?\d*', '', name)
        name = re.sub(r'\d+\.?\d*\s*per\s*100g', '', name)
        name = re.sub(r'\d+\.?\d*\s*each', '', name)
        
        # Add spaces between quantity and brand (e.g., "200gAl'Fez" -> "200g Al'Fez")
        name = re.sub(r'(\d+g)([A-Z])', r'\1 \2', name)
        name = re.sub(r'(\d+kg)([A-Z])', r'\1 \2', name)
        name = re.sub(r'(\d+ml)([A-Z])', r'\1 \2', name)
        name = re.sub(r'(\d+l)([A-Z])', r'\1 \2', name)
        
        # Add spaces between brand and product (e.g., "Al'FezMoroccan" -> "Al'Fez Moroccan")
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        
        # Clean up multiple spaces
        name = re.sub(r'\s+', ' ', name)
        
        # Remove "more sizes" and similar text
        name = re.sub(r'\d+\s+more\s+sizes?', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\d+\s+more\s+size', '', name, flags=re.IGNORECASE)
        
        # Handle specific Heinz multipack patterns
        # "415g6Heinz Baked Beans1 13 more sizes" -> "Heinz Baked Beans Family Pack"
        if "415g6Heinz" in name and "Baked Beans" in name:
            name = "Heinz Baked Beans Family Pack"
        # "400g6Heinz Classic Cream of Tomato Soup Family Pack" -> "Heinz Classic Cream of Tomato Soup Family Pack"
        elif "400g6Heinz" in name and "Family Pack" in name:
            name = name.replace("400g6Heinz", "Heinz ")
        # "550g Heinz Chilli Black Beans Family Pack Mexican-Style" -> "Heinz Chilli Black Beans Family Pack Mexican-Style"
        elif "550g Heinz" in name and "Family Pack" in name:
            name = name.replace("550g ", "")
        
        # Handle Branston multipack patterns
        # "410g4BranstonBaked Beans in Tomato Sauce" -> "Branston Baked Beans in Tomato Sauce 4 x 410g"
        if "410g4Branston" in name and "Baked Beans" in name:
            name = name.replace("410g4Branston", "Branston ")
            if "in Tomato Sauce" in name:
                name = "Branston Baked Beans in Tomato Sauce 4 x 410g"
            elif "Reduced Salt and Sugar" in name or "Reduced Sugar" in name:
                name = "Branston Baked Beans Reduced Salt and Sugar 4 x 410g"
        
        # Remove trailing numbers and special characters
        name = re.sub(r'\s*\d+\s*$', '', name)
        name = re.sub(r'[^\w\s\'-]', ' ', name)
        
        # Clean up multiple spaces
        name = re.sub(r'\s+', ' ', name)
        
        return name.strip()
    
    def _is_multipack(self, product_name: str) -> bool:
        """Check if product is a multipack"""
        import re
        multipack_patterns = [
            r'\d+\s*x\s*\d+',  # "6 x 415g"
            r'\d+\s*pack',     # "6 pack"
            r'\d+\s*cans?',    # "6 cans"
            r'\d+\s*bottles?', # "6 bottles"
            r'\d+\s*pieces?',  # "6 pieces"
            r'\d+\s*items?',   # "6 items"
        ]
        
        # Check for multipack patterns
        for pattern in multipack_patterns:
            if re.search(pattern, product_name, re.IGNORECASE):
                return True
        
        # Check for "Family Pack" which is a common multipack indicator
        if "family pack" in product_name.lower():
            return True
        
        # Check for "multipack" keyword
        if "multipack" in product_name.lower():
            return True
        
        return False
    
    def _generate_multipack_terms(self, product_name: str, brand: str) -> List[str]:
        """Generate multipack-specific search terms"""
        terms = []
        
        # Extract quantity and pack size
        quantity, pack_size = self._extract_quantity_and_pack_size(product_name)
        
        if pack_size > 1:
            # Term 1: "Family Pack" (common multipack term)
            if brand:
                terms.append(f"{brand} Family Pack")
            
            # Term 1.5: "Baked Beans Family Pack" (more specific)
            if "beanz" in product_name.lower():
                terms.append(f"{brand} Baked Beans Family Pack")
            
            # Term 2: "6 pack" format
            if quantity:
                terms.append(f"{brand} {int(pack_size)} pack")
            
            # Term 3: "multipack" format
            if brand:
                terms.append(f"{brand} multipack")
            
            # Term 4: "Baked Beans" instead of "Beanz" (more common)
            if "beanz" in product_name.lower():
                terms.append(f"{brand} Baked Beans {pack_size} x {int(quantity)}g")
            
            # Term 5: Simplified multipack term
            if brand:
                terms.append(f"{brand} {pack_size} pack")
        
        return terms
    
    def _extract_product_url(self, card) -> str:
        """Extract product URL from card"""
        link = card.find('a')
        if link and link.get('href'):
            href = link['href']
            if href.startswith('http'):
                return href
            else:
                return "https://www.trolley.co.uk" + href
        return ""
    
    def _calculate_similarity_improved(self, name1: str, name2: str) -> float:
        """Calculate similarity with much more lenient matching"""
        # Convert to lowercase for comparison
        name1_lower = name1.lower()
        name2_lower = name2.lower()
        
        # Extract brand and product name from both
        brand1, product1 = self._extract_brand_and_product(name1)
        brand2, product2 = self._extract_brand_and_product(name2)
        
        # Clean product names for comparison
        product1_clean = self._clean_product_name_for_comparison(product1)
        product2_clean = self._clean_product_name_for_comparison(product2)
        
        # Handle case where one or both are just brand names (no product)
        if not product1_clean and not product2_clean:
            # Both are just brand names - compare brands only
            if brand1 and brand2 and self._are_brands_similar(brand1, brand2):
                return 0.8  # High similarity for matching brands
            else:
                return 0.0
        elif not product1_clean or not product2_clean:
            # One is just a brand name - check if it matches the other's brand
            if not product1_clean and brand1 and brand2 and self._are_brands_similar(brand1, brand2):
                return 0.6  # Good similarity for brand match
            elif not product2_clean and brand1 and brand2 and self._are_brands_similar(brand1, brand2):
                return 0.6  # Good similarity for brand match
            else:
                return 0.0
        
        # Both have product names - calculate normal similarity
        # Split into words
        words1 = set(product1_clean.split())
        words2 = set(product2_clean.split())
        
        if not words1 or not words2:
            return 0.0
        
        # Calculate Jaccard similarity with word variations
        intersection = words1.intersection(words2)
        
        # Check for word variations (e.g., "cous" vs "couscous")
        for word1 in words1:
            for word2 in words2:
                if word1 != word2:
                    # Check if one word is contained in the other
                    if word1 in word2 or word2 in word1:
                        intersection.add(word1)
                        intersection.add(word2)
        
        union = words1.union(words2)
        jaccard_similarity = len(intersection) / len(union)
        
        # Bonus for exact substring matches (case insensitive)
        if product1_clean in product2_clean or product2_clean in product1_clean:
            jaccard_similarity += 0.2
        
        # Bonus for "Family Pack" matches (common multipack term)
        if "family pack" in name1_lower and "family pack" in name2_lower:
            jaccard_similarity += 0.5  # Increased bonus for Family Pack matches
        elif "family pack" in name1_lower or "family pack" in name2_lower:
            # One has Family Pack, the other doesn't - this is important for multipacks
            if self._is_multipack(name1_lower) or self._is_multipack(name2_lower):
                jaccard_similarity += 0.3  # Bonus for multipack + Family Pack combination
        
        # BONUS for multipack matching - if both are multipacks, give extra bonus
        if self._is_multipack(name1_lower) and self._is_multipack(name2_lower):
            jaccard_similarity += 0.4  # Significant bonus for multipack-to-multipack matching
        
        # Bonus for "Baked Beans" vs "Beanz" matches
        if ("baked beans" in name1_lower and "beanz" in name2_lower) or \
           ("beanz" in name1_lower and "baked beans" in name2_lower):
            jaccard_similarity += 0.2
        
        # BONUS for "Baked Beans" product type matches - ensure baked beans match baked beans
        if ("baked beans" in name1_lower and "baked beans" in name2_lower) or \
           ("beanz" in name1_lower and "beanz" in name2_lower):
            jaccard_similarity += 0.6  # Very strong bonus for matching baked beans products
        
        # BONUS for exact product type matches (regular vs regular, reduced vs reduced)
        if ("reduced sugar" in name1_lower and "reduced sugar" in name2_lower) or \
           ("reduced salt" in name1_lower and "reduced salt" in name2_lower):
            jaccard_similarity += 0.3  # Bonus for matching variants
        elif ("reduced sugar" not in name1_lower and "reduced salt" not in name1_lower) and \
             ("reduced sugar" not in name2_lower and "reduced salt" not in name2_lower):
            # Both are regular products (no reduced sugar/salt)
            if "baked beans" in name1_lower and "baked beans" in name2_lower:
                jaccard_similarity += 0.3  # Bonus for regular baked beans match
        
        # PENALTY for "Chilli Black Beans" vs "Baked Beans" - they are different products
        if ("chilli black beans" in name1_lower and ("baked beans" in name2_lower or "beanz" in name2_lower)) or \
           (("baked beans" in name1_lower or "beanz" in name1_lower) and "chilli black beans" in name2_lower):
            jaccard_similarity -= 0.5  # Heavy penalty for different bean types
        
        # PENALTY for "Cream of Tomato Soup" vs "Baked Beans" - they are completely different products
        if ("cream of tomato soup" in name1_lower and ("baked beans" in name2_lower or "beanz" in name2_lower)) or \
           (("baked beans" in name1_lower or "beanz" in name1_lower) and "cream of tomato soup" in name2_lower):
            jaccard_similarity -= 0.8  # Very heavy penalty for completely different product types
        
        # PENALTY for "Curry Chickpeas" vs "Baked Beans" - they are completely different products
        if ("curry chickpeas" in name1_lower and ("baked beans" in name2_lower or "beanz" in name2_lower)) or \
           (("baked beans" in name1_lower or "beanz" in name1_lower) and "curry chickpeas" in name2_lower):
            jaccard_similarity -= 0.9  # Very heavy penalty for completely different product types
        
        # PENALTY for any "Chickpeas" vs "Baked Beans" - they are different product categories
        if ("chickpeas" in name1_lower and ("baked beans" in name2_lower or "beanz" in name2_lower)) or \
           (("baked beans" in name1_lower or "beanz" in name1_lower) and "chickpeas" in name2_lower):
            jaccard_similarity -= 0.8  # Heavy penalty for different product categories
        
                # PENALTY for "reduced sugar salt" vs regular products - they are different variants
        if ("reduced sugar" in name1_lower or "reduced salt" in name1_lower) and \
           ("reduced sugar" not in name2_lower and "reduced salt" not in name2_lower):
            jaccard_similarity -= 0.6  # Heavy penalty for variant mismatch
        elif ("reduced sugar" in name2_lower or "reduced salt" in name2_lower) and \
              ("reduced sugar" not in name1_lower and "reduced salt" not in name1_lower):
            jaccard_similarity -= 0.6  # Heavy penalty for variant mismatch
        
        # PENALTY for multipack vs single product mismatch
        if self._is_multipack(name1_lower) and not self._is_multipack(name2_lower):
            jaccard_similarity -= 0.5  # Heavy penalty for multipack vs single mismatch
        elif not self._is_multipack(name1_lower) and self._is_multipack(name2_lower):
            jaccard_similarity -= 0.5  # Heavy penalty for single vs multipack mismatch
        
        # STRICT BRAND MATCHING: Different brands should never match
        if brand1 and brand2:
            if self._are_brands_similar(brand1, brand2):
                # Same brand - give bonus
                jaccard_similarity += 0.5
            else:
                # Different brands - REJECT completely
                return 0.0  # Zero similarity for different brands
        elif brand1 or brand2:
            # One has a brand, the other doesn't - be cautious
            jaccard_similarity *= 0.3  # Reduce similarity significantly
        
        # Bonus for quantity tolerance (can be negative for pack size mismatches)
        quantity_bonus = self._calculate_quantity_similarity(name1, name2)
        jaccard_similarity += quantity_bonus
        
        # Ensure final similarity is between 0 and 1
        return max(0.0, min(1.0, jaccard_similarity))
    
    def _get_retailer_prices_fixed(self, product_url: str) -> Dict[str, Dict]:
        """Get prices from different retailers with improved extraction - optimized for speed"""
        try:
            # Check cache first
            cached_prices = self.cache_manager.get_price_data(product_url)
            if cached_prices:
                print(f"        📋 Using cached price data for: {product_url}")
                return cached_prices
            
            print(f"        Getting retailer prices from: {product_url}")
            
            headers = self.session.headers.copy()
            headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            
            response = self.session.get(product_url, headers=headers, timeout=15)  # Reduced timeout
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                price_data = self._parse_retailer_prices_fixed(soup)
                
                # Cache the price data
                self.cache_manager.set_price_data(product_url, price_data)
                
                return price_data
            else:
                print(f"        ❌ Failed to get product page: HTTP {response.status_code}")
                return {}
                
        except Exception as e:
            logging.getLogger(__name__).warning(f"Error getting retailer prices: {e}")
            return {}
    
    def _parse_retailer_prices_fixed(self, soup: BeautifulSoup) -> Dict[str, Dict]:
        """Parse retailer prices with improved extraction - optimized for speed"""
        retailer_prices = {}
        
        print(f"        Parsing retailer prices...")
        
        # Get the full page text for analysis - only once
        page_text = soup.get_text()
        
        # Look for specific retailer prices with better patterns - optimized order
        # Check most common retailers first for speed
        priority_retailers = ['Tesco', 'Morrisons', 'Ocado', 'Sainsbury\'s']
        other_retailers = ['ASDA', 'Wilko', 'Co-op']
        
        # Check priority retailers first
        for retailer in priority_retailers:
            if retailer in self.target_retailers:
                price = self._extract_retailer_price_fast(page_text, retailer)
                if price:
                    retailer_prices[retailer] = {
                        'name': retailer,
                        'price': price,
                        'price_per_unit': '',
                        'currency': 'GBP'
                    }
                    print(f"        Found {retailer}: £{price}")
                    # Early exit if we found Tesco (most important)
                    if retailer == 'Tesco':
                        break
        
        # Check other retailers only if we didn't find priority ones
        if not retailer_prices:
            for retailer in other_retailers:
                if retailer in self.target_retailers:
                    price = self._extract_retailer_price_fast(page_text, retailer)
                    if price:
                        retailer_prices[retailer] = {
                            'name': retailer,
                            'price': price,
                            'price_per_unit': '',
                            'currency': 'GBP'
                        }
                        print(f"        Found {retailer}: £{price}")
        
        # If we found any prices, return them
        if retailer_prices:
            print(f"        Found prices for retailers: {list(retailer_prices.keys())}")
        
        return retailer_prices
    
    def _extract_retailer_price_fast(self, page_text: str, retailer: str) -> Optional[float]:
        """Fast price extraction for a specific retailer"""
        import re
        
        # Optimized patterns for faster matching
        patterns = [
            rf'{re.escape(retailer)}[^£]*?£\s*(\d+\.?\d*)',
            rf'£\s*(\d+\.?\d*)[^£]*?{re.escape(retailer)}',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                return float(matches[0])
        
        return None
    
    def _extract_brand_and_product(self, product_name: str) -> Tuple[str, str]:
        """Extract brand and product name from product name"""
        if not product_name:
            return "", ""
        
        # Known brands to look for (in order of specificity - longer names first)
        known_brands = [
            'Dr. Oetker', 'Dr Oetker', 'Charlie Bigham\'s', 'Ainsley Harriott', 'Nojo Tahir',
            'Alfez', 'Al-fez', 'Al Fez', 'ALFEZ', 'Al\'Fez', 'Baxters', 'Kelloggs',
            'Great Scot', 'Colman\'s', 'Daddies', 'Marshalls', 'Natures Fi',
            'Fray Bento', 'Wagamama', 'WAGAMAMA', 'Coca Cola', 'Coca-Cola', 
            'Dr Pepper', 'Ko-Lee', 'Schwartz', 'Heinz', 'Koka',
            'Tesco', 'ASDA', 'Sainsburys', 'Sainsbury', 'Ocado', 'Morrisons', 
            'Co-op', 'Coop', 'Walkers', 'Pepsi', 'Fanta', 'Sprite', '7UP', 
            'Lay\'s', 'Pringles', 'Doritos', 'Oetker'
        ]
        
        product_lower = product_name.lower()
        
        # First, try to find known brands
        for brand in known_brands:
            brand_lower = brand.lower()
            if brand_lower in product_lower:
                # Extract the product part (everything after the brand)
                brand_start = product_lower.find(brand_lower)
                product_part = product_name[brand_start + len(brand):].strip()
                
                # Clean up the product part
                product_part = re.sub(r'^\s*[-–—]\s*', '', product_part)  # Remove leading dash
                product_part = product_part.strip()
                
                return brand, product_part
        
        # If no known brand found, try to extract first word as brand (but skip quantities and common words)
        words = product_name.split()
        if len(words) > 1:
            # Skip the first word if it looks like a quantity
            first_word = words[0]
            if re.match(r'^\d+\.?\d*(g|kg|ml|l|oz|lb|pack|packs|pieces?|items?)$', first_word, re.IGNORECASE):
                # First word is a quantity, try second word as brand
                if len(words) > 2:
                    potential_brand = words[1]
                    product_part = ' '.join(words[2:])
                    return potential_brand, product_part
                else:
                    return "", product_name
            else:
                # Check if first word looks like a brand (capitalized, not a common word)
                common_words = {'moroccan', 'italian', 'french', 'spanish', 'greek', 'indian', 'chinese', 'japanese', 'thai', 'mexican', 'mediterranean', 'middle', 'eastern', 'western', 'northern', 'southern', 'organic', 'natural', 'fresh', 'premium', 'deluxe', 'classic', 'traditional', 'modern', 'authentic', 'original', 'special', 'extra', 'super', 'mega', 'mini', 'small', 'large', 'big', 'tiny', 'giant', 'family', 'single', 'double', 'triple', 'multi', 'mixed', 'assorted', 'variety', 'selection', 'collection', 'range', 'series', 'line', 'brand', 'product', 'food', 'drink', 'beverage', 'snack', 'meal', 'dish', 'recipe', 'style', 'flavor', 'flavour', 'taste', 'aroma', 'scent', 'fragrance', 'spice', 'herb', 'seasoning', 'sauce', 'dressing', 'dip', 'spread', 'paste', 'puree', 'jam', 'jelly', 'marmalade', 'syrup', 'honey', 'sugar', 'salt', 'pepper', 'oil', 'vinegar', 'juice', 'water', 'milk', 'cream', 'cheese', 'yogurt', 'yoghurt', 'butter', 'bread', 'cake', 'cookie', 'biscuit', 'cracker', 'chip', 'crisp', 'nut', 'seed', 'grain', 'cereal', 'pasta', 'rice', 'bean', 'pea', 'lentil', 'chickpea', 'vegetable', 'fruit', 'meat', 'fish', 'chicken', 'beef', 'pork', 'lamb', 'turkey', 'duck', 'seafood', 'shellfish', 'crustacean', 'mollusk', 'mollusc', 'egg', 'dairy', 'vegan', 'vegetarian', 'gluten', 'free', 'wheat', 'rye', 'barley', 'oat', 'corn', 'maize', 'potato', 'tomato', 'onion', 'garlic', 'ginger', 'chili', 'chilli', 'pepper', 'paprika', 'cumin', 'coriander', 'turmeric', 'curry', 'masala', 'tandoori', 'kebab', 'shish', 'shawarma', 'falafel', 'hummus', 'tabbouleh', 'couscous', 'cous', 'couscous', 'quinoa', 'bulgur', 'farro', 'spelt', 'millet', 'sorghum', 'teff', 'amaranth', 'buckwheat', 'kamut', 'triticale', 'durum', 'semolina', 'polenta', 'grits', 'hominy', 'cornmeal', 'flour', 'meal', 'powder', 'granule', 'flake', 'chip', 'piece', 'slice', 'chunk', 'cube', 'dice', 'shred', 'grate', 'mince', 'chop', 'dice', 'slice', 'cut', 'whole', 'half', 'quarter', 'third', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth', 'dozen', 'pack', 'bottle', 'can', 'jar', 'box', 'bag', 'tub', 'pot', 'carton', 'sachet', 'pouch', 'wrapper', 'container', 'package', 'bundle', 'set', 'kit', 'collection', 'assortment', 'variety', 'selection', 'range', 'series', 'line', 'brand', 'product', 'item', 'goods', 'merchandise', 'stock', 'inventory', 'supply', 'provision', 'ration', 'portion', 'serving', 'helping', 'plate', 'bowl', 'cup', 'glass', 'mug', 'tumbler', 'bottle', 'can', 'jar', 'box', 'bag', 'tub', 'pot', 'carton', 'sachet', 'pouch', 'wrapper', 'container', 'package', 'bundle', 'set', 'kit', 'collection', 'assortment', 'variety', 'selection', 'range', 'series', 'line', 'brand', 'product', 'item', 'goods', 'merchandise', 'stock', 'inventory', 'supply', 'provision', 'ration', 'portion', 'serving', 'helping', 'plate', 'bowl', 'cup', 'glass', 'mug', 'tumbler'}
                
                if first_word.lower() in common_words:
                    # First word is a common word, treat as product name
                    return "", product_name
                else:
                    # First word might be a brand, use it as brand
                    potential_brand = words[0]
                    product_part = ' '.join(words[1:])
                    return potential_brand, product_part
        
        return "", product_name
    
    def _extract_quantity(self, product_name: str) -> str:
        """Extract quantity from product name"""
        import re
        quantity_match = re.search(r'\b(\d+\.?\d*)\s*(g|kg|ml|l|oz|lb|pack|packs|pieces?|items?)\b', product_name, re.IGNORECASE)
        if quantity_match:
            return f"{quantity_match.group(1)}{quantity_match.group(2)}"
        return ""
    
    def _extract_brand(self, product_name: str) -> str:
        """Extract brand from product name"""
        brand, _ = self._extract_brand_and_product(product_name)
        return brand
    
    def _are_brands_similar(self, brand1: str, brand2: str) -> bool:
        """Check if two brands are similar variations - STRICT MATCHING"""
        brand1_lower = brand1.lower().strip()
        brand2_lower = brand2.lower().strip()
        
        # Exact match
        if brand1_lower == brand2_lower:
            return True
        
        # Handle ONLY known legitimate variations (very strict)
        brand_variations = {
            'alfez': ['al-fez', 'al fez', 'al\'fez'],
            'al-fez': ['alfez', 'al fez', 'al\'fez'],
            'al fez': ['alfez', 'al-fez', 'al\'fez'],
            'al\'fez': ['alfez', 'al-fez', 'al fez'],
            'dr. oetker': ['dr oetker', 'oetker'],
            'dr oetker': ['dr. oetker', 'oetker'],
            'oetker': ['dr. oetker', 'dr oetker'],
            'sainsburys': ['sainsbury'],
            'sainsbury': ['sainsburys'],
            'wagamama': ['wagamama'],
            'coca cola': ['coca-cola'],
            'coca-cola': ['coca cola'],
        }
        
        # Check if brands are in the same variation group
        for main_brand, variations in brand_variations.items():
            if brand1_lower == main_brand and brand2_lower in variations:
                return True
            if brand2_lower == main_brand and brand1_lower in variations:
                return True
            if brand1_lower in variations and brand2_lower in variations:
                return True
        
        # For all other cases - brands are NOT similar
        return False
    
    def _clean_product_name_for_comparison(self, product_name: str) -> str:
        """Clean product name for comparison"""
        import re
        
        if not product_name:
            return ""
        
        # Remove quantities
        clean_name = re.sub(r'\b\d+\.?\d*\s*(g|kg|ml|l|oz|lb|pack|packs|pieces?|items?)\b', '', product_name, flags=re.IGNORECASE)
        
        # Remove special characters but keep spaces and hyphens
        clean_name = re.sub(r'[^\w\s-]', ' ', clean_name)
        
        # Normalize multiple spaces
        clean_name = re.sub(r'\s+', ' ', clean_name)
        
        # Trim whitespace
        clean_name = clean_name.strip()
        
        return clean_name
    
    def _calculate_quantity_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity bonus for quantities with strict pack size matching"""
        import re
        
        # Extract quantities and pack sizes from both names
        quantity1, pack_size1 = self._extract_quantity_and_pack_size(name1)
        quantity2, pack_size2 = self._extract_quantity_and_pack_size(name2)
        
        # If no quantities found, no bonus
        if quantity1 is None or quantity2 is None:
            return 0.0
        
        # STRICT PACK SIZE MATCHING: Pack sizes must match exactly
        if pack_size1 != pack_size2:
            # Different pack sizes (e.g., 6 pack vs single) - heavily penalize
            return -0.5  # Negative bonus to reduce similarity
        
        # If pack sizes match, check individual quantities
        if pack_size1 == pack_size2:
            # Same pack size - check if quantities are similar
            if quantity1 == quantity2:
                return 0.3  # Exact match
            elif abs(quantity1 - quantity2) / max(quantity1, quantity2) <= 0.1:  # 10% tolerance
                return 0.2  # Very close match
            elif abs(quantity1 - quantity2) / max(quantity1, quantity2) <= 0.2:  # 20% tolerance
                return 0.1  # Close match
            else:
                return -0.2  # Different quantities - penalize
        
        return 0.0
    
    def _extract_quantity_value(self, product_name: str) -> Optional[float]:
        """Extract numeric quantity value from product name"""
        import re
        quantity_match = re.search(r'\b(\d+\.?\d*)\s*(g|kg|ml|l|oz|lb|pack|packs|pieces?|items?)\b', product_name, re.IGNORECASE)
        if quantity_match:
            return float(quantity_match.group(1))
        return None
    
    def _extract_quantity_and_pack_size(self, product_name: str) -> Tuple[Optional[float], int]:
        """
        Extract quantity and pack size from product name
        
        Returns:
            Tuple of (quantity_value, pack_size)
            pack_size = 1 for single items, >1 for multipacks
        """
        import re
        
        # Look for multipack patterns first (e.g., "6 x 415g", "4 pack", "6 cans")
        multipack_patterns = [
            r'(\d+)\s*x\s*(\d+\.?\d*)\s*(g|kg|ml|l|oz|lb)',  # "6 x 415g"
            r'(\d+)\s*pack',  # "6 pack"
            r'(\d+)\s*cans?',  # "6 cans"
            r'(\d+)\s*bottles?',  # "6 bottles"
            r'(\d+)\s*pieces?',  # "6 pieces"
            r'(\d+)\s*items?',  # "6 items"
        ]
        
        for pattern in multipack_patterns:
            match = re.search(pattern, product_name, re.IGNORECASE)
            if match:
                pack_size = int(match.group(1))
                if len(match.groups()) > 1 and match.group(2):
                    # Has individual quantity (e.g., "6 x 415g")
                    quantity = float(match.group(2))
                else:
                    # No individual quantity specified (e.g., "6 pack")
                    quantity = None
                return quantity, pack_size
        
        # Look for single item patterns
        single_patterns = [
            r'(\d+\.?\d*)\s*(g|kg|ml|l|oz|lb)',  # "415g", "1.5kg"
            r'(\d+\.?\d*)\s*pack',  # "1 pack" (single)
            r'(\d+\.?\d*)\s*can',  # "1 can" (single)
            r'(\d+\.?\d*)\s*bottle',  # "1 bottle" (single)
        ]
        
        for pattern in single_patterns:
            match = re.search(pattern, product_name, re.IGNORECASE)
            if match:
                quantity = float(match.group(1))
                return quantity, 1  # Single item
        
        # No quantity found
        return None, 1
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache_manager.clear_cache()
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return self.cache_manager.get_cache_stats()
    
    def print_cache_stats(self):
        """Print cache statistics"""
        self.cache_manager.print_cache_stats()
