"""Flask web application for Privacy-Preserving Face Authentication"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
from pathlib import Path
import sys
from datetime import datetime
import base64
import re
import logging

# Add project root to path so `src` package resolves reliably
BASE_DIR = Path(__file__).parent
sys.path.append(str(BASE_DIR))

from src.config import UPLOAD_FOLDER, SECRET_KEY, MAX_FILE_SIZE
from src.config import ADMIN_USERNAME, ADMIN_PASSWORD, AUTHENTICATION_THRESHOLD, REQUIRE_USERNAME_LOGIN
from src.authentication.enroll_face import FaceEnrollment
from src.authentication.authenticate_face import FaceAuthentication
from src.database.db_manager import DatabaseManager, get_user_by_username
from src.database.store_templates import TemplateStorage
from src.preprocessing.validate_image import ImageValidator
from src.face_detection.detect_face import detect_face_in_image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_email(email):
    """Validate email format"""
    if not email:
        return True  # Email is optional
    
    # Simple email validation regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False
    return True


# Initialize Flask app
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create upload folder
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

# Initialize components
db = DatabaseManager()

# Initialize shared HE context once for entire application
from src.encryption.he_context import create_he_context
try:
    shared_he_context = create_he_context()
    logger.info("[OK] Shared HE context initialized for entire application")
except Exception as e:
    logger.warning(f"Could not initialize shared HE context: {e}")
    shared_he_context = None

enrollment_system = FaceEnrollment(shared_he_context)
auth_system = FaceAuthentication(shared_he_context)
image_validator = ImageValidator()

# Initialize admin user
def init_admin():
    """Initialize default admin user"""
    try:
        conn = db.connect()
        cursor = conn.cursor()
        
        # Check if admin exists
        cursor.execute('SELECT * FROM admin_users WHERE username = ?', (ADMIN_USERNAME,))
        if not cursor.fetchone():
            # Create admin
            password_hash = generate_password_hash(ADMIN_PASSWORD)
            cursor.execute('''
                INSERT INTO admin_users (username, password_hash)
                VALUES (?, ?)
            ''', (ADMIN_USERNAME, password_hash))
            conn.commit()
            logger.info("Default admin user created")
    except Exception as e:
        logger.error(f"Error initializing admin: {e}")

init_admin()


def save_image_from_data_url(data_url, prefix):
    """Save a base64 data URL image to the uploads folder and return path."""
    if not data_url:
        return None, "No image captured"

    # Improve regex to handle more data URL formats
    match = re.match(r'^data:image\/(png|jpeg|jpg|webp);base64,(.+)$', data_url)
    if not match:
        print(f"[DEBUG] Invalid data URL format. First 100 chars: {data_url[:100]}")
        return None, "Invalid image data format"

    ext = match.group(1).lower()
    if ext == 'jpeg':
        ext = 'jpg'
    elif ext == 'webp':
        ext = 'jpg'  # Convert webp to jpg

    image_b64 = match.group(2)
    try:
        # Decode base64
        image_bytes = base64.b64decode(image_b64)
        print(f"[DEBUG] Base64 decoded successfully: {len(image_bytes)} bytes")
    except Exception as e:
        print(f"[DEBUG] Base64 decode error: {e}")
        return None, "Invalid base64 image data"

    if len(image_bytes) == 0:
        return None, "Image data is empty"

    if len(image_bytes) > MAX_FILE_SIZE:
        return None, f"Image exceeds maximum size ({len(image_bytes)} bytes > {MAX_FILE_SIZE} bytes)"

    # Save file
    filename = secure_filename(f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}")
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        
        # Verify file was written
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            print(f"[DEBUG] Image saved: {filepath} ({os.path.getsize(filepath)} bytes)")
            return filepath, None
        else:
            return None, "Failed to save image file"
    except Exception as e:
        print(f"[DEBUG] File write error: {e}")
        return None, f"Error saving image: {str(e)}"


def login_required(f):
    """Decorator for routes that require admin login"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    
    return decorated_function


# ==================== PUBLIC ROUTES ====================

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/enroll', methods=['GET', 'POST'])
def enroll():
    """User enrollment page"""
    if request.method == 'POST':
        try:
            # Get form data
            username = request.form.get('username', '').strip()
            full_name = request.form.get('full_name', '').strip()
            email = request.form.get('email', '').strip()
            image_data = request.form.get('image_data', '')
            
            # Check required fields
            if not username:
                flash('Username is required', 'error')
                return redirect(url_for('enroll'))
            
            # Check if username already exists
            existing_user = get_user_by_username(username)
            if existing_user:
                flash(f'Username "{username}" already exists. Please choose a different username.', 'error')
                return redirect(url_for('enroll'))
            
            # Validate email format if provided
            if email and not validate_email(email):
                flash('Invalid email format. Please use a valid email address (e.g., user@example.com)', 'error')
                return redirect(url_for('enroll'))
            
            # Save captured image from webcam
            filepath, error_message = save_image_from_data_url(image_data, f"{username}_enroll")
            if error_message:
                flash(f'Capture failed: {error_message}', 'error')
                return redirect(url_for('enroll'))
            
            logger.info(f"Captured image saved: {filepath}")
            
            # Validate image contains face
            is_valid, message = image_validator.validate_uploaded_image(filepath)
            
            if not is_valid:
                os.remove(filepath)  # Delete invalid image
                flash(f'Image rejected: {message}', 'error')
                return redirect(url_for('enroll'))

            # Pre-check if face already enrolled
            matched, match_info, error_message = auth_system.find_existing_user_by_face(filepath)
            if error_message:
                os.remove(filepath)
                flash(error_message, 'error')
                return redirect(url_for('enroll'))
            if matched:
                os.remove(filepath)
                existing_user = match_info.get('username', 'Unknown')
                flash(f'Already enrolled as {existing_user}.', 'error')
                return redirect(url_for('enroll'))
            
            # CRITICAL: Explicit face detection before enrollment
            face_found, detected_face = detect_face_in_image(filepath)
            if not face_found:
                os.remove(filepath)
                logger.warning(f"REJECTED: No face detected in enrollment image")
                flash('Face is not properly visible. Please try again with a clear face image.', 'error')
                return redirect(url_for('enroll'))
            
            # Enroll user
            success, result_message = enrollment_system.enroll_user(
                username, filepath, full_name, email
            )
            
            if success:
                flash(f'Enrollment successful! {result_message}', 'success')
                return redirect(url_for('index'))
            else:
                flash(f'Enrollment failed: {result_message}', 'error')
                os.remove(filepath)
                return redirect(url_for('enroll'))
        
        except Exception as e:
            logger.error(f"Enrollment error: {e}")
            flash(f'Error during enrollment: {str(e)}', 'error')
            return redirect(url_for('enroll'))
    
    return render_template('enroll.html')


@app.route('/api/pre_enroll', methods=['POST'])
def api_pre_enroll():
    """Pre-enrollment check: validate face visibility and existing enrollment"""
    image_data = request.form.get('image_data', '')

    filepath, error_message = save_image_from_data_url(image_data, "pre_enroll")
    if error_message:
        return jsonify({
            "ok": False,
            "face_visible": False,
            "message": error_message
        })

    try:
        is_valid, message = image_validator.validate_uploaded_image(filepath)
        if not is_valid:
            return jsonify({
                "ok": False,
                "face_visible": False,
                "message": message
            })

        matched, match_info, error_message = auth_system.find_existing_user_by_face(filepath)
        if error_message:
            return jsonify({
                "ok": False,
                "face_visible": True,
                "message": error_message
            })

        if matched:
            return jsonify({
                "ok": False,
                "face_visible": True,
                "already_enrolled": True,
                "username": match_info.get('username'),
                "similarity_score": match_info.get('similarity_score')
            })

        return jsonify({
            "ok": True,
            "face_visible": True
        })

    finally:
        try:
            os.remove(filepath)
        except Exception:
            pass


@app.route('/authenticate', methods=['GET', 'POST'])
def authenticate():
    """User authentication page"""
    if request.method == 'POST':
        try:
            # Get username (optional)
            username = request.form.get('username', '').strip()
            image_data = request.form.get('image_data', '')
            
            # Enforce username requirement if configured
            if REQUIRE_USERNAME_LOGIN and not username:
                flash('Username is required for authentication', 'error')
                return redirect(url_for('authenticate'))
            
            # Save captured image from webcam
            filepath, error_message = save_image_from_data_url(image_data, "auth")
            if error_message:
                flash(f'Capture failed: {error_message}', 'error')
                return redirect(url_for('authenticate'))
            
            logger.info(f"Authentication capture saved: {filepath}")
            
            # Validate image contains face
            is_valid, message = image_validator.validate_uploaded_image(filepath)
            
            if not is_valid:
                os.remove(filepath)
                flash(f'Image rejected: {message}', 'error')
                return redirect(url_for('authenticate'))
            
            # CRITICAL: Explicit face detection before authentication
            face_found, detected_face = detect_face_in_image(filepath)
            if not face_found:
                os.remove(filepath)
                logger.warning(f"REJECTED: No face detected in authentication image")
                flash('Authentication failed: No human face detected in the image', 'error')
                return redirect(url_for('authenticate'))
            
            # Authenticate
            success, result_info = auth_system.authenticate(
                filepath, username if username else None
            )
            
            # Clean up
            os.remove(filepath)
            
            if success:
                user = result_info.get('username', 'Unknown')
                score = result_info.get('similarity_score', 0)
                
                # Additional security check: verify score is not suspiciously low
                # Even if it passes threshold, reject if it looks like a false positive
                if score < 0.50:
                    logger.warning(f"REJECTED: Score {score:.4f} is suspiciously low (below 0.50 safety threshold)")
                    db.add_auth_log(user, 'failed', score)
                    flash(f'Authentication failed: Quality score too low ({score:.4f}). This may not be a valid match.', 'error')
                    return redirect(url_for('authenticate'))
                
                # Log successful authentication
                db.add_auth_log(user, 'success', score)
                logger.info(f"[AUTH SUCCESS] User {user} authenticated with score {score:.4f}")
                flash(f'Authentication successful! Welcome, {user} (Score: {score:.4f})', 'success')
                return render_template('auth_success.html', user_info=result_info)
            else:
                message = result_info.get('message', 'Authentication failed')
                best_score = result_info.get('similarity_score', 0)
                db.add_auth_log('unknown', 'failed', best_score)
                logger.info(f"[AUTH FAILED] {message}")
                flash(f'Authentication failed: {message}', 'error')
                return redirect(url_for('authenticate'))
        
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            flash(f'Error during authentication: {str(e)}', 'error')
            return redirect(url_for('authenticate'))
    
    return render_template('authenticate.html')


# ==================== ADMIN ROUTES ====================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        try:
            conn = db.connect()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM admin_users WHERE username = ?', (username,))
            admin = cursor.fetchone()
            
            if admin and check_password_hash(admin[2], password):
                session['admin_logged_in'] = True
                session['admin_username'] = username
                
                # Update last login
                cursor.execute('''
                    UPDATE admin_users SET last_login = CURRENT_TIMESTAMP 
                    WHERE username = ?
                ''', (username,))
                conn.commit()
                
                flash('Admin login successful', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid credentials', 'error')
        
        except Exception as e:
            logger.error(f"Admin login error: {e}")
            flash('Login error', 'error')
    
    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    users = db.get_all_users(active_only=False)
    logs = db.get_auth_logs(limit=50)
    
    stats = {
        'total_users': len(users),
        'active_users': sum(1 for u in users if u['is_active']),
        'inactive_users': sum(1 for u in users if not u['is_active']),
        'recent_logins': len([l for l in logs if l['auth_result'] == 'success'])
    }
    
    return render_template('admin_dashboard.html', 
                         users=users, logs=logs, stats=stats)


@app.route('/admin/users')
@login_required
def admin_users():
    """Admin user management"""
    users = db.get_all_users(active_only=False)
    template_storage = TemplateStorage(db)
    
    # Add template count to each user
    for user in users:
        user['template_count'] = template_storage.count_user_templates(user['user_id'])
    
    return render_template('admin_users.html', users=users)


@app.route('/admin/user/<int:user_id>/toggle', methods=['POST'])
@login_required
def admin_toggle_user(user_id):
    """Toggle user active status"""
    try:
        # Get current status
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT is_active FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        
        if row:
            new_status = not row[0]
            db.update_user_status(user_id, new_status)
            status_text = "activated" if new_status else "deactivated"
            flash(f'User {status_text} successfully', 'success')
        else:
            flash('User not found', 'error')
    
    except Exception as e:
        logger.error(f"Error toggling user: {e}")
        flash('Error updating user status', 'error')
    
    return redirect(url_for('admin_users'))


@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    """Delete user"""
    try:
        if db.delete_user(user_id):
            flash('User deleted successfully', 'success')
        else:
            flash('Error deleting user', 'error')
    
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        flash('Error deleting user', 'error')
    
    return redirect(url_for('admin_users'))


@app.route('/admin/logs')
@login_required
def admin_logs():
    """Admin authentication logs"""
    logs = db.get_auth_logs(limit=200)
    return render_template('admin_logs.html', logs=logs)


# ==================== API ROUTES ====================

@app.route('/api/validate_image', methods=['POST'])
def api_validate_image():
    """API endpoint to validate if webcam capture contains a face"""
    image_data = request.form.get('image_data', '')
    try:
        filepath, error_message = save_image_from_data_url(image_data, "temp")
        if error_message:
            return jsonify({'valid': False, 'message': error_message}), 400
        
        # Validate
        is_valid, message = image_validator.validate_uploaded_image(filepath)
        
        # Clean up
        os.remove(filepath)
        
        return jsonify({'valid': is_valid, 'message': message})
    
    except Exception as e:
        return jsonify({'valid': False, 'message': str(e)}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("Privacy-Preserving Face Authentication System")
    print("=" * 60)
    print(f"Admin credentials:")
    print(f"  Username: {ADMIN_USERNAME}")
    print(f"  Password: {ADMIN_PASSWORD}")
    print("=" * 60)
    print(f"Authentication threshold: {AUTHENTICATION_THRESHOLD}")
    print("=" * 60)
    print("Starting Flask application...")
    print("Access at: http://localhost:5000")
    print("=" * 60)
    
    app.run(debug=False, host='127.0.0.1', port=5000)
