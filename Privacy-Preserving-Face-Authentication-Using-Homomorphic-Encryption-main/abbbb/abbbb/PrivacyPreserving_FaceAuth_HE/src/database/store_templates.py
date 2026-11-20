"""Template storage for encrypted face embeddings"""
from src.database.db_manager import DatabaseManager


class TemplateStorage:
    """Manages encrypted template storage"""
    
    def __init__(self, db_manager=None):
        self.db = db_manager or DatabaseManager()
    
    def store_template(self, user_id, encrypted_template):
        """Store encrypted template for user"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO templates (user_id, encrypted_template) VALUES (?, ?)',
                (user_id, encrypted_template)
            )
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def retrieve_template(self, user_id):
        """Retrieve encrypted template for user"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            cursor.execute(
                'SELECT encrypted_template FROM templates WHERE user_id = ? ORDER BY created_at DESC LIMIT 1',
                (user_id,)
            )
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else None
        except Exception:
            return None

    def count_user_templates(self, user_id):
        """Count templates for a user"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM templates WHERE user_id = ?', (user_id,))
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception:
            return 0
