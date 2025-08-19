"""
Trolley.co.uk Scraper Package
============================

A web scraper for extracting product prices from Trolley.co.uk
"""

from .trolley_scraper_fixed import FixedTrolleyScraper
from .cache_manager import CacheManager
from .constants import REQUEST_HEADER
from .filemanager import Config

__all__ = ['FixedTrolleyScraper', 'CacheManager', 'REQUEST_HEADER', 'Config']
