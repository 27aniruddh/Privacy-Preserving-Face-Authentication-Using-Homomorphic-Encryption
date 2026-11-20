"""Database manager for SQLite operations"""
import sqlite3
from pathlib import Path
from src.config import DATABASE_PATH

class DatabaseManager:
    """Manages SQLite database operations"""
    
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_db()
    
    def connect(self):
        """Connect to database"""
        conn = sqlite3.connect(str(self.db_path))
        return conn
    
    def init_db(self):
        """Initialize database tables"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    full_name TEXT,
                    email TEXT,
                    is_active INTEGER DEFAULT 1,
                    user_id INTEGER
                )
            ''')
            
            # Create templates table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS templates (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    encrypted_template BLOB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')
            
            # Create admin_users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin_users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')
            
            # Create authentication_logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS authentication_logs (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    status TEXT,
                    similarity REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Ensure required columns exist (for older databases)
            cursor.execute("PRAGMA table_info(users)")
            existing_columns = {row[1] for row in cursor.fetchall()}
            if 'full_name' not in existing_columns:
                cursor.execute('ALTER TABLE users ADD COLUMN full_name TEXT')
            if 'email' not in existing_columns:
                cursor.execute('ALTER TABLE users ADD COLUMN email TEXT')
            if 'is_active' not in existing_columns:
                cursor.execute('ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1')
            if 'user_id' not in existing_columns:
                cursor.execute('ALTER TABLE users ADD COLUMN user_id INTEGER')
                cursor.execute('UPDATE users SET user_id = id WHERE user_id IS NULL')
            
            # Ensure admin_users has last_login column
            cursor.execute("PRAGMA table_info(admin_users)")
            admin_columns = {row[1] for row in cursor.fetchall()}
            if 'last_login' not in admin_columns:
                cursor.execute('ALTER TABLE admin_users ADD COLUMN last_login TIMESTAMP')
            
            conn.commit()
            conn.close()
            print("[OK] Database initialized")
        except Exception as e:
            print(f"[ERROR] Database initialization error: {e}")
    
    def get_user(self, username):
        """Get user by username"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            conn.close()
            return user
        except Exception as e:
            print(f"[ERROR] Error getting user: {e}")
            return None
    
    def get_all_users(self, active_only=False):
        """Get all users"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            if active_only:
                cursor.execute('''
                    SELECT id, username, full_name, email, is_active, created_at
                    FROM users WHERE is_active = 1
                ''')
            else:
                cursor.execute('''
                    SELECT id, username, full_name, email, is_active, created_at
                    FROM users
                ''')
            rows = cursor.fetchall()
            conn.close()

            users = []
            for row in rows:
                users.append({
                    'user_id': row[0],
                    'username': row[1],
                    'full_name': row[2],
                    'email': row[3],
                    'is_active': bool(row[4]),
                    'created_at': row[5]
                })
            return users
        except Exception as e:
            print(f"[ERROR] Error getting users: {e}")
            return []
    
    def add_user(self, username, full_name=None, email=None):
        """Add a new user"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, full_name, email, is_active)
                VALUES (?, ?, ?, 1)
            ''', (username, full_name, email))
            user_id = cursor.lastrowid
            cursor.execute('UPDATE users SET user_id = ? WHERE id = ?', (user_id, user_id))
            conn.commit()
            conn.close()
            print(f"[OK] User {username} created in database with ID {user_id}")
            return user_id
        except sqlite3.IntegrityError as e:
            print(f"[ERROR] Duplicate username: {username} already exists in database")
            return None
        except Exception as e:
            print(f"[ERROR] Unexpected database error adding user {username}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def toggle_user_status(self, user_id):
        """Toggle user active status"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute('SELECT is_active FROM users WHERE id = ?', (user_id,))
            result = cursor.fetchone()
            if result:
                new_status = 0 if result[0] else 1
                cursor.execute('UPDATE users SET is_active = ? WHERE id = ?', (new_status, user_id))
                conn.commit()
                conn.close()
                return True
            conn.close()
            return False
        except Exception as e:
            print(f"[ERROR] Error toggling user status: {e}")
            return False
    
    def delete_user(self, user_id):
        """Delete a user and their templates"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM templates WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[ERROR] Error deleting user: {e}")
            return False

    def get_auth_logs(self, limit=200):
        """Get recent authentication logs"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT username, status, similarity, created_at
                FROM authentication_logs
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            rows = cursor.fetchall()
            conn.close()

            logs = []
            for row in rows:
                logs.append({
                    'username': row[0],
                    'status': row[1],
                    'auth_result': row[1],
                    'similarity': row[2],
                    'created_at': row[3]
                })
            return logs
        except Exception as e:
            print(f"[ERROR] Error getting logs: {e}")
            return []
    
    def add_auth_log(self, username, status, similarity):
        """Add authentication log"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO authentication_logs (username, status, similarity)
                VALUES (?, ?, ?)
            ''', (username, status, similarity))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[ERROR] Error adding auth log: {e}")
            return False
    
    def get_stats(self):
        """Get dashboard statistics"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            # Total users
            cursor.execute('SELECT COUNT(*) FROM users')
            total_users = cursor.fetchone()[0]
            
            # Active users
            cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1')
            active_users = cursor.fetchone()[0]
            
            # Inactive users
            inactive_users = total_users - active_users
            
            # Recent logins (last 24 hours)
            cursor.execute('''
                SELECT COUNT(*) FROM authentication_logs 
                WHERE status = 'success' 
                AND datetime(created_at) >= datetime('now', '-1 day')
            ''')
            recent_logins = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'inactive_users': inactive_users,
                'recent_logins': recent_logins
            }
        except Exception as e:
            print(f"[ERROR] Error getting stats: {e}")
            return {
                'total_users': 0,
                'active_users': 0,
                'inactive_users': 0,
                'recent_logins': 0
            }


# Backward compatibility - standalone functions
def get_user(username):
    db = DatabaseManager()
    return db.get_user(username)

def get_user_by_username(username):
    """Alias for get_user"""
    db = DatabaseManager()
    return db.get_user(username)

def get_connection():
    """Get database connection"""
    db = DatabaseManager()
    return db.connect()

def get_all_users(active_only=False):
    db = DatabaseManager()
    return db.get_all_users(active_only)

def add_user(username, full_name=None, email=None):
    db = DatabaseManager()
    return db.add_user(username, full_name, email)

def create_user(username, full_name=None, email=None):
    """Alias for add_user"""
    db = DatabaseManager()
    return db.add_user(username, full_name, email)
