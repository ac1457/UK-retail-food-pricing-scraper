#!/usr/bin/env python3
"""
Cache Manager for Trolley Scraper
=================================
Manages caching of scraped product data to avoid re-scraping
"""

import json
import os
import hashlib
import time
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
import logging
from pathlib import Path


class CacheManager:
    """Manages caching of scraped product data"""
    
    def __init__(self, cache_dir: str = "cache", cache_duration_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.cache_duration = timedelta(hours=cache_duration_hours)
        self.cache_duration_hours = cache_duration_hours  # Store as instance variable
        
        if not self.cache_dir.exists():
            self.cache_dir.mkdir(parents=True)
        
        # Old cache files are no longer used for direct loading, but for cleanup
        self.search_cache_file = self.cache_dir / "search_cache.json"
        self.price_cache_file = self.cache_dir / "price_cache.json"
        
        self.search_cache = {} # Placeholder, actual cache is file-based
        self.price_cache = {}  # Placeholder, actual cache is file-based
    
    def _load_cache(self, cache_file: Path) -> Dict:
        """Load cache from file"""
        try:
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    # Clean expired entries
                    return self._clean_expired_entries(cache)
            return {}
        except Exception as e:
            logging.getLogger(__name__).warning(f"Warning: Could not load cache from {cache_file}: {e}")
            return {}
    
    def _save_cache(self, cache: Dict, cache_file: Path):
        """Save cache to file"""
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.getLogger(__name__).warning(f"Warning: Could not save cache to {cache_file}: {e}")
    
    def _clean_expired_entries(self, cache: Dict) -> Dict:
        """Remove expired cache entries"""
        current_time = datetime.now()
        cleaned_cache = {}
        
        for key, entry in cache.items():
            if 'timestamp' in entry:
                entry_time = datetime.fromisoformat(entry['timestamp'])
                if current_time - entry_time < self.cache_duration:
                    cleaned_cache[key] = entry
        
        return cleaned_cache
    
    def _generate_cache_key(self, data: str) -> str:
        """Generate a cache key from data"""
        return hashlib.md5(data.encode('utf-8')).hexdigest()
    
    def _is_cache_valid(self, cache_file: Path) -> bool:
        """Check if cache file is still valid (not expired)"""
        try:
            if not cache_file.exists():
                return False
            
            # Check file modification time
            file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
            current_time = datetime.now()
            
            # Check if file is within cache duration
            if current_time - file_time < self.cache_duration:
                return True
            
            # Also check the timestamp inside the file if it exists
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    if isinstance(cache_data, dict) and 'timestamp' in cache_data:
                        cache_time = datetime.fromisoformat(cache_data['timestamp'])
                        return current_time - cache_time < self.cache_duration
            except:
                pass
            
            return False
            
        except Exception as e:
            logging.getLogger(__name__).warning(f"Error checking cache validity: {e}")
            return False
    
    def get_search_results(self, product_name: str) -> Optional[List[Dict]]:
        """Get cached search results for a product"""
        try:
            cache_key = self._generate_cache_key(product_name)
            cache_file = self.cache_dir / f"{cache_key}.json"
            
            if cache_file.exists():
                # Check if cache is still valid
                if self._is_cache_valid(cache_file):
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cached_data = json.load(f)
                    
                    # Validate cached data structure
                    if isinstance(cached_data, dict) and 'results' in cached_data:
                        results = cached_data['results']
                        if isinstance(results, list):
                            print(f"📋 Cache hit for: {product_name} ({len(results)} results)")
                            return results
                    
                    print(f"⚠️ Invalid cache data for: {product_name}")
                    return None
                else:
                    print(f"⏰ Cache expired for: {product_name}")
                    return None
            else:
                return None
                
        except Exception as e:
            logging.getLogger(__name__).warning(f"Error reading cache: {e}")
            return None
    
    def set_search_results(self, product_name: str, results: List[Dict]) -> None:
        """Cache search results for a product"""
        try:
            cache_key = self._generate_cache_key(product_name)
            cache_file = self.cache_dir / f"{cache_key}.json"
            
            # Create cache data with metadata
            cache_data = {
                'product_name': product_name,
                'results': results,
                'timestamp': datetime.now().isoformat(),
                'cache_duration_hours': self.cache_duration_hours,
                'source': 'enhanced_workflow'
            }
            
            # Ensure cache directory exists
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            
            # Write cache file
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Cached {len(results)} results for: {product_name}")
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Error writing cache: {e}")
    
    def get_price_data(self, url: str) -> Optional[Dict]:
        """Get cached price data for a URL"""
        try:
            cache_key = self._generate_cache_key(url)
            cache_file = self.cache_dir / f"price_{cache_key}.json"
            
            if cache_file.exists() and self._is_cache_valid(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                
                if isinstance(cached_data, dict) and 'retailer_prices' in cached_data:
                    print(f"📋 Price cache hit for: {url}")
                    return cached_data['retailer_prices']
                
            return None
            
        except Exception as e:
            logging.getLogger(__name__).warning(f"Error reading price cache: {e}")
            return None
    
    def set_price_data(self, url: str, retailer_prices: Dict) -> None:
        """Cache price data for a URL"""
        try:
            cache_key = self._generate_cache_key(url)
            cache_file = self.cache_dir / f"price_{cache_key}.json"
            
            cache_data = {
                'url': url,
                'retailer_prices': retailer_prices,
                'timestamp': datetime.now().isoformat(),
                'cache_duration_hours': self.cache_duration_hours
            }
            
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Cached price data for: {url}")
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Error writing price cache: {e}")
    
    def clear_cache(self):
        """Clear all cached data"""
        self.search_cache = {}
        self.price_cache = {}
        
        # Remove cache files
        for cache_file in [self.search_cache_file, self.price_cache_file]:
            if cache_file.exists():
                cache_file.unlink()
        
        print("🗑️ Cache cleared")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        try:
            if not self.cache_dir.exists():
                return {'total_files': 0, 'search_caches': 0, 'price_caches': 0, 'total_size_mb': 0}
            
            files = list(self.cache_dir.glob('*.json'))
            search_caches = len([f for f in files if not f.name.startswith('price_')])
            price_caches = len([f for f in files if f.name.startswith('price_')])
            
            total_size = sum(f.stat().st_size for f in files)
            total_size_mb = total_size / (1024 * 1024)
            
            return {
                'total_files': len(files),
                'search_caches': search_caches,
                'price_caches': price_caches,
                'total_size_mb': round(total_size_mb, 2)
            }
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Error getting cache stats: {e}")
            return {'error': str(e)}
    
    def print_cache_stats(self):
        """Print cache statistics"""
        stats = self.get_cache_stats()
        
        if 'error' in stats:
            print(f"❌ Error getting cache stats: {stats['error']}")
            return
        
        print(f"\n📊 CACHE STATISTICS")
        print(f"=" * 30)
        print(f"Total cache files: {stats['total_files']}")
        print(f"Search caches: {stats['search_caches']}")
        print(f"Price caches: {stats['price_caches']}")
        print(f"Total cache size: {stats['total_size_mb']} MB")
        print(f"Cache duration: {self.cache_duration_hours} hours")
        print(f"=" * 30)
