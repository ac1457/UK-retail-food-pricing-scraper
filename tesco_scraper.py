#!/usr/bin/env python3
"""
Direct Tesco.com Scraper
========================

High-accuracy price extraction directly from Tesco.com
"""

import re
import time
import random
import logging
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from curl_cffi import Session
import urllib.parse

from constants import REQUEST_HEADER


class TescoScraper:
    """Direct scraper for Tesco.com"""
    
    def __init__(self):
        """Initialize Tesco scraper"""
        self.session = Session()
        self.session.headers.update(REQUEST_HEADER)
        self.session.impersonate = "chrome120"
        self.base_url = "https://www.tesco.com"
    
    def search_product(self, product_name: str) -> Optional[Dict]:
        """Search for product on Tesco.com"""
        try:
            # Generate search URL
            search_term = self._clean_search_term(product_name)
            search_url = f"{self.base_url}/groceries/en-GB/search?query={search_term}"
            
            print(f"🔍 Tesco: Searching {search_url}")
            
            headers = self.session.headers.copy()
            headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            
            response = self.session.get(search_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                return self._extract_product_info(soup, product_name)
            else:
                print(f"❌ Tesco: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logging.getLogger(__name__).error(f"Tesco search error: {e}")
            return None
    
    def _clean_search_term(self, product_name: str) -> str:
        """Clean product name for Tesco search"""
        # Remove special characters but keep spaces and hyphens
        clean_name = re.sub(r'[^\w\s-]', ' ', product_name)
        clean_name = re.sub(r'\s+', ' ', clean_name)
        clean_name = clean_name.strip()
        
        return urllib.parse.quote(clean_name)
    
    def _extract_product_info(self, soup: BeautifulSoup, original_product_name: str) -> Optional[Dict]:
        """Extract product information from Tesco search results"""
        try:
            # Look for product cards
            product_cards = soup.find_all('div', {'data-auto': 'product-tile'})
            
            if not product_cards:
                # Try alternative selectors
                product_cards = soup.find_all('div', class_=re.compile(r'product.*card|tile.*product'))
            
            best_match = None
            best_similarity = 0.0
            
            for card in product_cards[:5]:  # Check first 5 products
                product_info = self._extract_from_card(card, original_product_name)
                if product_info and product_info['similarity_score'] > best_similarity:
                    best_similarity = product_info['similarity_score']
                    best_match = product_info
            
            if best_match and best_similarity >= 0.15:  # Minimum threshold
                print(f"✅ Tesco: Found match with similarity {best_similarity:.3f}")
                return best_match
            else:
                print(f"❌ Tesco: No good matches found")
                return None
                
        except Exception as e:
            logging.getLogger(__name__).error(f"Tesco extraction error: {e}")
            return None
    
    def _extract_from_card(self, card, original_product_name: str) -> Optional[Dict]:
        """Extract product info from a single card"""
        try:
            # Extract product name
            name_elem = card.find('span', {'data-auto': 'product-name'})
            if not name_elem:
                name_elem = card.find('h3') or card.find('h4') or card.find('a')
            
            if not name_elem:
                return None
            
            product_name = name_elem.get_text().strip()
            if not product_name:
                return None
            
            # Extract price
            price_elem = card.find('span', {'data-auto': 'price-value'})
            if not price_elem:
                price_elem = card.find(class_=re.compile(r'price|cost'))
            
            price = None
            if price_elem:
                price_text = price_elem.get_text().strip()
                price_match = re.search(r'£(\d+\.?\d*)', price_text)
                if price_match:
                    price = float(price_match.group(1))
            
            # Extract URL
            link_elem = card.find('a')
            product_url = None
            if link_elem and link_elem.get('href'):
                href = link_elem['href']
                if href.startswith('http'):
                    product_url = href
                else:
                    product_url = self.base_url + href
            
            # Calculate similarity
            similarity_score = self._calculate_similarity(product_name, original_product_name)
            
            return {
                'name': product_name,
                'price': price,
                'url': product_url,
                'similarity_score': similarity_score,
                'retailer': 'Tesco',
                'source': 'direct'
            }
            
        except Exception as e:
            logging.getLogger(__name__).warning(f"Tesco card extraction error: {e}")
            return None
    
    def _calculate_similarity(self, product_name: str, original_name: str) -> float:
        """Calculate similarity between product names"""
        # Simple word-based similarity
        words1 = set(product_name.lower().split())
        words2 = set(original_name.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
