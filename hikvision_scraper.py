"""
Hikvision Product Selector - Data Import System
Imports and syncs Hikvision product data from Excel files.

NOTE: Hikvision's product selector website uses JavaScript rendering without a public API,
making direct web scraping unreliable. This system uses Excel imports instead:
- Import HIKVISION Excel files with product specifications
- Parse and structure data according to Hikvision filter categories  
- Sync to database for use in the product selector interface

For updates: Download latest product list from Hikvision and re-import the Excel file.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
from typing import List, Dict, Optional
import sqlite3
from datetime import datetime

class HikvisionScraper:
    """Scrapes product data from Hikvision product selector"""
    
    BASE_URL = "https://www.hikvision.com"
    SELECTOR_URL = f"{BASE_URL}/en/products/product-selector/"
    
    # Hikvision filter categories (as per their website)
    FILTER_CATEGORIES = {
        'case_type': ['Box', 'Bullet', 'Cube', 'Dome', 'Fisheye', 'Mini PT', 
                      'Panoramic Dome', 'PTZ Dome', 'Specialty', 'Turret'],
        'resolution': ['2 MP', '3 MP', '4 MP', '5 MP', '6 MP', '8 MP', 
                      '12 MP', '16 MP', '26 MP', '32 MP'],
        'lens_type': ['Fixed Lens', 'Manual Varifocal Lens', 
                     'Motorized Varifocal Lens', 'Multi-Lens'],
        'ai_features': ['AIOP', 'Face Capture', 'Face Recognition', 
                       'Hardhat Detection', 'Heat Map', 'License Plate Recognition (ANPR)',
                       'Metadata', 'Multi-target-type Detection', 'On/Off Duty Detection',
                       'People Counting', 'Perimeter Protection', 'Queue Management'],
        'environmental_protection': ['IK08', 'IK10', 'IP54', 'IP65', 'IP66', 
                                     'IP67', 'IP68', 'NEMA 4X'],
        'illumination_distance': ['0-20m', '21-50m', '51-100m', '101-300m'],
        'low_light_imaging': ['ColorVu', 'Darkfighter', 'Darkfighter S', 
                             'Darkfighter X', 'Powered by Darkfighter'],
        'power_supply': ['12 VDC', '24 VAC', '24 VDC', '36 VDC', 'PoE', 'PoE+'],
        'storage_type': ['EMMC', 'SD Card', 'SSD'],
        'supplemental_light': ['IR Light', 'Smart Hybrid Light', 'White Light'],
        'wdr': ['120 dB', '130 dB', '140 dB', '150 dB', 'DWDR'],
        'wireless_network': ['4G', '5G', 'Wi-Fi']
    }
    
    def __init__(self, db_path='ProjectStatus.db'):
        """Initialize scraper"""
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/html, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': self.BASE_URL
        })
        
    def fetch_products(self, limit: int = 100) -> List[Dict]:
        """
        Fetch products from Hikvision website
        
        Args:
            limit: Maximum number of products to fetch
            
        Returns:
            List of product dictionaries
        """
        print(f"🔍 Fetching products from Hikvision...")
        
        try:
            response = self.session.get(self.SELECTOR_URL, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            products = []
            
            # Find product cards/items in the page
            # Note: This is a template - actual selectors need to be adjusted based on site structure
            product_items = soup.find_all('div', class_=['product-item', 'product-card'])
            
            print(f"📦 Found {len(product_items)} product elements")
            
            for item in product_items[:limit]:
                try:
                    product = self._parse_product_element(item)
                    if product:
                        products.append(product)
                except Exception as e:
                    print(f"  ⚠️  Error parsing product: {e}")
                    continue
            
            print(f"✅ Successfully parsed {len(products)} products")
            return products
            
        except Exception as e:
            print(f"❌ Error fetching products: {e}")
            return []
    
    def _parse_product_element(self, element) -> Optional[Dict]:
        """Parse individual product element"""
        product = {
            'model_number': '',
            'name': '',
            'description': '',
            'case_type': 'N/A',
            'resolution': 'N/A',
            'lens_type': 'N/A',
            'ai_features': 'N/A',
            'environmental_protection': 'N/A',
            'illumination_distance': 'N/A',
            'low_light_imaging': 'N/A',
            'power_supply': 'N/A',
            'storage_type': 'N/A',
            'supplemental_light': 'N/A',
            'wdr': 'N/A',
            'wireless_network': 'N/A',
            'price': 0.0,
            'url': '',
            'image_url': '',
            'scraped_at': datetime.now().isoformat()
        }
        
        # Extract model number (usually in a specific class or data attribute)
        model_elem = element.find(['h3', 'h4', 'a'], class_=re.compile(r'model|title|name', re.I))
        if model_elem:
            product['model_number'] = model_elem.get_text(strip=True)
        
        # Extract description
        desc_elem = element.find(['p', 'div'], class_=re.compile(r'desc|detail', re.I))
        if desc_elem:
            product['description'] = desc_elem.get_text(strip=True)
        
        # Extract URL
        link_elem = element.find('a', href=True)
        if link_elem:
            href = link_elem['href']
            product['url'] = href if href.startswith('http') else f"{self.BASE_URL}{href}"
        
        # Extract image
        img_elem = element.find('img')
        if img_elem and img_elem.get('src'):
            src = img_elem['src']
            product['image_url'] = src if src.startswith('http') else f"{self.BASE_URL}{src}"
        
        return product if product['model_number'] else None
    
    def sync_to_database(self, products: List[Dict]) -> int:
        """
        Sync scraped products to database
        
        Args:
            products: List of product dictionaries
            
        Returns:
            Number of products synced
        """
        if not products:
            print("⚠️  No products to sync")
            return 0
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Create table if not exists
        c.execute('''
            CREATE TABLE IF NOT EXISTS hikvision_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_number TEXT UNIQUE NOT NULL,
                name TEXT,
                description TEXT,
                case_type TEXT,
                resolution TEXT,
                lens_type TEXT,
                ai_features TEXT,
                environmental_protection TEXT,
                illumination_distance TEXT,
                low_light_imaging TEXT,
                power_supply TEXT,
                storage_type TEXT,
                supplemental_light TEXT,
                wdr TEXT,
                wireless_network TEXT,
                price REAL DEFAULT 0.0,
                url TEXT,
                image_url TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        synced_count = 0
        
        for product in products:
            try:
                c.execute('''
                    INSERT OR REPLACE INTO hikvision_products 
                    (model_number, name, description, case_type, resolution, lens_type,
                     ai_features, environmental_protection, illumination_distance,
                     low_light_imaging, power_supply, storage_type, supplemental_light,
                     wdr, wireless_network, price, url, image_url, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    product['model_number'],
                    product.get('name', product['model_number']),
                    product.get('description', ''),
                    product.get('case_type', 'N/A'),
                    product.get('resolution', 'N/A'),
                    product.get('lens_type', 'N/A'),
                    product.get('ai_features', 'N/A'),
                    product.get('environmental_protection', 'N/A'),
                    product.get('illumination_distance', 'N/A'),
                    product.get('low_light_imaging', 'N/A'),
                    product.get('power_supply', 'N/A'),
                    product.get('storage_type', 'N/A'),
                    product.get('supplemental_light', 'N/A'),
                    product.get('wdr', 'N/A'),
                    product.get('wireless_network', 'N/A'),
                    product.get('price', 0.0),
                    product.get('url', ''),
                    product.get('image_url', '')
                ))
                synced_count += 1
            except Exception as e:
                print(f"  ⚠️  Error syncing product {product.get('model_number', 'unknown')}: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"✅ Synced {synced_count} products to database")
        return synced_count
    
    def get_filter_options(self) -> Dict:
        """Get available filter options from database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        filter_options = {}
        
        for category in ['case_type', 'resolution', 'lens_type', 'power_supply', 
                        'low_light_imaging', 'supplemental_light', 'wdr', 'wireless_network']:
            c.execute(f"SELECT DISTINCT {category} FROM hikvision_products WHERE {category} != 'N/A' ORDER BY {category}")
            options = [row[0] for row in c.fetchall() if row[0]]
            if options:
                filter_options[category] = options
        
        conn.close()
        return filter_options


def manual_sync():
    """Manual sync function for testing"""
    print("=" * 80)
    print("🚀 HIKVISION PRODUCT SYNC")
    print("=" * 80)
    print()
    
    scraper = HikvisionScraper()
    
    print("📥 Fetching products from Hikvision...")
    products = scraper.fetch_products(limit=100)
    
    if products:
        print(f"\n💾 Syncing {len(products)} products to database...")
        synced = scraper.sync_to_database(products)
        print(f"\n✅ Sync complete! {synced} products updated.")
    else:
        print("\n⚠️  No products fetched. Check your internet connection or scraper configuration.")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    manual_sync()
