"""
Setup and Installation Script for Privacy-Preserving Face Authentication System
Run this script to verify installation and setup the system
"""

import sys
import subprocess
import os
from pathlib import Path

print("=" * 70)
print("Privacy-Preserving Face Authentication System")
print("Setup and Verification Script")
print("=" * 70)
print()

# Check Python version
print("1. Checking Python version...")
if sys.version_info < (3, 8):
    print("   ❌ Python 3.8 or higher is required")
    print(f"   Current version: {sys.version}")
    sys.exit(1)
else:
    print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
print()

# Check and install dependencies
print("2. Checking dependencies...")
required_packages = [
    'flask',
    'tensorflow',
    'opencv-python',
    'numpy',
    'tenseal'
]

missing_packages = []
for package in required_packages:
    try:
        __import__(package.replace('-', '_'))
        print(f"   ✅ {package}")
    except ImportError:
        print(f"   ❌ {package} (not installed)")
        missing_packages.append(package)

if missing_packages:
    print()
    print(f"   Missing packages: {', '.join(missing_packages)}")
    print(f"   Run: pip install {' '.join(missing_packages)}")
    print(f"   Or: pip install -r requirements.txt")
    print()
else:
    print()
    print("   ✅ All dependencies installed!")
print()

# Create necessary directories
print("3. Verifying directory structure...")
base_dir = Path(__file__).parent
directories = [
    'dataset/enrollment_faces',
    'dataset/auth_faces',
    'dataset/rejected_faces',
    'models',
    'outputs/encrypted_templates',
    'outputs/logs',
    'outputs/results',
    'uploads',
    'static',
    'templates'
]

for dir_path in directories:
    full_path = base_dir / dir_path
    if full_path.exists():
        print(f"   ✅ {dir_path}")
    else:
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {dir_path} (created)")
print()

# Check source code modules
print("4. Checking source code modules...")
src_modules = [
    'src/config.py',
    'src/face_detection/detect_face.py',
    'src/preprocessing/validate_image.py',
    'src/feature_extraction/extract_embedding.py',
    'src/encryption/he_context.py',
    'src/database/db_manager.py',
    'src/authentication/enroll_face.py',
    'src/authentication/authenticate_face.py'
]

all_modules_exist = True
for module in src_modules:
    module_path = base_dir / module
    if module_path.exists():
        print(f"   ✅ {module}")
    else:
        print(f"   ❌ {module} (missing)")
        all_modules_exist = False

if not all_modules_exist:
    print()
    print("   ⚠️  Some source modules are missing!")
    print("   Please ensure all source files are in place.")
print()

# Check templates
print("5. Checking HTML templates...")
templates = [
    'templates/base.html',
    'templates/index.html',
    'templates/enroll.html',
    'templates/authenticate.html',
    'templates/admin_dashboard.html'
]

all_templates_exist = True
for template in templates:
    template_path = base_dir / template
    if template_path.exists():
        print(f"   ✅ {template}")
    else:
        print(f"   ❌ {template} (missing)")
        all_templates_exist = False

if not all_templates_exist:
    print()
    print("   ⚠️  Some templates are missing!")
print()

# Test imports
print("6. Testing module imports...")
try:
    sys.path.append(str(base_dir / "src"))
    
    from src.config import DATABASE_PATH
    print("   ✅ config.py")
    
    from src.face_detection.detect_face import FaceDetector
    print("   ✅ face_detection module")
    
    from src.preprocessing.validate_image import ImageValidator
    print("   ✅ preprocessing module")
    
    from src.encryption.he_context import HEContext
    print("   ✅ encryption module")
    
    from src.database.db_manager import DatabaseManager
    print("   ✅ database module")
    
    from src.authentication.enroll_face import FaceEnrollment
    print("   ✅ authentication module")
    
    print()
    print("   ✅ All modules imported successfully!")
    
except Exception as e:
    print()
    print(f"   ❌ Import error: {e}")
    print("   Some modules may have issues.")

print()

# Summary
print("=" * 70)
print("Setup Summary")
print("=" * 70)

if not missing_packages and all_modules_exist and all_templates_exist:
    print("✅ System is ready to run!")
    print()
    print("To start the application:")
    print("  python app.py")
    print()
    print("Then open your browser to: http://localhost:5000")
    print()
    print("Default admin credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print()
    print("⚠️  Remember to change admin password in production!")
else:
    print("⚠️  Setup incomplete - please resolve the issues above")
    print()
    if missing_packages:
        print("Install missing packages:")
        print("  pip install -r requirements.txt")
    print()
    print("For detailed instructions, see README.md or QUICKSTART.md")

print("=" * 70)
