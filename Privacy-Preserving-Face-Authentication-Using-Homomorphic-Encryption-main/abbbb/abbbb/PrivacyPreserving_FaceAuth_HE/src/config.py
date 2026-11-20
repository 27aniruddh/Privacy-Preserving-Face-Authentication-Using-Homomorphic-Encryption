"""Configuration settings for the Face Authentication System"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Upload folder
UPLOAD_FOLDER = BASE_DIR / "uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16 MB

# Secret key for Flask sessions
SECRET_KEY = "your-secret-key-change-in-production-9a8b7c6d5e4f3a2b1c0d"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Authentication settings
AUTHENTICATION_THRESHOLD = 0.85  # Similarity threshold for login
PRE_ENROLLMENT_THRESHOLD = 0.99  # EXTREMELY HIGH - virtually never blocks (99%+ required)
REQUIRE_USERNAME_LOGIN = False  # Whether to require username during login
SKIP_DUPLICATE_CHECK = True     # Set to False to enable pre-enrollment duplicate check

# Database
DATABASE_PATH = BASE_DIR / "face_auth.db"
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

# Face detection
FACE_DETECTION_SCALE = 1.3
FACE_DETECTION_MIN_NEIGHBORS = 5

# Encryption
ENCRYPTION_SCHEME = "ckks"  # Cheon-Kim-Kim-Song scheme
POLY_MODULUS_DEGREE = 4096
COEFF_MOD_BIT_SIZES = [60, 40, 40, 60]
SCALE = 2 ** 40

print(f"[OK] Configuration loaded from: {BASE_DIR}")
