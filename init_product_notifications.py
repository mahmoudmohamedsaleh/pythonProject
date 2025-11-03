"""
Initialize product notification event codes
Run this script to ensure product.edited and product.deleted events are registered
"""
import sqlite3

def init_product_notifications(db_path='ProjectStatus.db'):
    """Initialize product notification event codes in the database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if notification_events table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notification_events'")
        if not cursor.fetchone():
            print("notification_events table does not exist. Skipping initialization.")
            return False
        
        # Insert product event codes if they don't exist
        cursor.execute("""
            INSERT OR IGNORE INTO notification_events (event_code, event_name, event_category, description, default_priority)
            VALUES 
              ('product.edited', 'Product Edited', 'product', 'A CCTV product was edited', 'normal'),
              ('product.deleted', 'Product Deleted', 'product', 'A CCTV product was deleted', 'high')
        """)
        
        rows_added = cursor.rowcount
        conn.commit()
        
        if rows_added > 0:
            print(f"✓ Initialized {rows_added} product notification event codes")
        else:
            print("✓ Product notification event codes already exist")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Error initializing product notifications: {e}")
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    init_product_notifications()
