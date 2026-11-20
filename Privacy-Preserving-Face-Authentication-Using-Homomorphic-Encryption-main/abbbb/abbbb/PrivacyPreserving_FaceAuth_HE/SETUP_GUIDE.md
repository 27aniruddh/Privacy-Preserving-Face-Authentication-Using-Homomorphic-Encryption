# Privacy-Preserving Face Authentication System - SETUP

## Overview
This is a complete face authentication system using:
- **DeepFace** with **Facenet512** for face embeddings (512-dimensional)
- **Homomorphic Encryption** for secure face template storage
- **SQLite** database for user management
- **Flask** web application

## Installation

### 1. Prerequisites
- Python 3.8+
- pip (Python package manager)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

This includes:
- Flask (web framework)
- DeepFace (face recognition)
- TenSEAL (homomorphic encryption)
- numpy, opencv, cryptography, etc.

### 3. Run the Application
```bash
python app.py
```

The app will start on `http://localhost:5000`

---

## First Run Setup

### 1. Clear Any Old Data (Important!)
```bash
rm face_auth.db          # Delete old database
rm aes.key               # Delete old encryption key
```

### 2. Start the Application
```bash
python app.py
```

The system will:
- Create a fresh `face_auth.db` database
- Generate new `aes.key` encryption key
- Create admin user (username: `admin`, password: `admin123`)

---

## User Workflow

### As a New User

1. **Go to `/enroll`**
   - Enter unique username (e.g., "john_doe")
   - Optionally: enter name and email
   - Click "Capture Face" - ensure good lighting, clear face
   - Click "Enroll"

2. **What Happens Behind the Scenes**
   - System extracts 512-dim face embedding from image
   - Embedding is encrypted with Homomorphic Encryption
   - Encrypted template is stored in database
   - User account is created

3. **Success** 
   - User is enrolled and ready to authenticate

### As an Enrolled User

1. **Go to `/authenticate`**
   - Optionally enter username (leave blank to auto-match)
   - Click "Capture Face"
   - Click "Authenticate"

2. **What Happens**
   - System extracts embedding from your face
   - Compares against all enrolled users' templates
   - Finds best match (must be ≥0.85 similarity)
   - Shows success with your details

### As Admin

1. **Go to `/admin/login`**
   - Username: `admin`
   - Password: `admin123`

2. **In Admin Dashboard**
   - View all enrolled users
   - View authentication logs
   - Deactivate/delete users
   - Change default admin password (recommended!)

---

## How Face Matching Works

### Similarity Scores

| Score Range | Meaning |
|---|---|
| 0.00 - 0.60 | Completely different face |
| 0.60 - 0.80 | Similar but different people |
| 0.80 - 0.90 | Could be same person with different lighting |
| 0.90 - 1.00 | Same person (very similar) |

### Thresholds

- **Pre-Enrollment Check: 0.95**
  - Only blocks if new face is >95% similar to existing user
  - Different people won't block each other
  - Prevents false "already enrolled" errors

- **Authentication: 0.85**
  - Accepts face if >85% similar to enrolled template
  - Allows for lighting/angle variations
  - Rejects unknown faces

---

## Testing the System

### Quick Test Scenario

```
1. Clear database: rm face_auth.db aes.key
2. Start app: python app.py
3. Enroll Person A (/enroll)
4. Enroll Person B (/enroll) - different person
5. Authenticate as Person A (/authenticate)
   -> Should show Person A's details
6. Authenticate as Person B (/authenticate)  
   -> Should show Person B's details
7. Try authenticating as random person
   -> Should show "Face not recognized"
```

### Check Console Output

The console shows debug information:

```
[DEBUG] Face detected! Embedding shape: (512,), range: [-0.25, 0.48]
[DEBUG] Pre-enroll check - User john_doe: similarity = 0.68
[DEBUG] Pre-enroll best match: john_doe with score 0.68, threshold: 0.95
[INFO] Pre-enroll ALLOWED: Best match to john_doe only 0.68 (below 0.95 threshold)
```

If similarity between different people is >0.90, the face detection is having issues.

---

## Troubleshooting

### Problem: "Already enrolled as [other user]" when enrolling new person

**Why**: Pre-enrollment check thinks new face matches existing user  
**Solution**:
- Ensure good lighting for new person
- Use different angle/expression than existing user
- If score shows <0.95 but still blocked, database may be corrupted - clear it

### Problem: Same person doesn't authenticate (score too low)

**Why**: Face detection quality varies by image  
**Solution**:
- Use same lighting as during enrollment
- Position face in center of frame
- Look straight at camera
- If consistent issue, re-enroll with better quality image

### Problem: Unknown face authenticates as someone (false positive)

**Why**: Unlikely but possible if faces are very similar  
**Solution**:
- Check console: what was the similarity score?
- If >0.90 for different people, embedding extraction is wrong
- Try re-enrolling users in different order
- If persists, clear database and start fresh

### Problem: Database corrupted or app crashes

**Solution**:
```bash
# Stop the app
# Delete old data:
rm face_auth.db
rm aes.key
# Start fresh:
python app.py
```

---

## Configuration

Edit `src/config.py` to change:

```python
AUTHENTICATION_THRESHOLD = 0.85      # Login threshold
PRE_ENROLLMENT_THRESHOLD = 0.95      # Duplicate check threshold
REQUIRE_USERNAME_LOGIN = False       # Force username for login
ADMIN_USERNAME = "admin"             # Admin username
ADMIN_PASSWORD = "admin123"          # Admin password (CHANGE THIS!)
```

---

## Files Structure

```
PrivacyPreserving_FaceAuth_HE/
├── app.py                      # Main Flask application
├── src/
│   ├── config.py              # Configuration settings
│   ├── authentication/
│   │   ├── enroll_face.py     # Enrollment logic
│   │   └── authenticate_face.py # Authentication logic
│   ├── face_detection/
│   │   └── detect_face.py     # Face extraction & comparison
│   ├── database/
│   │   ├── db_manager.py      # Database operations
│   │   └── store_templates.py # Template storage
│   ├── encryption/
│   │   └── he_context.py      # Homomorphic encryption
│   └── preprocessing/
│       └── validate_image.py  # Image validation
├── templates/                  # HTML templates
│   ├── enroll.html
│   ├── authenticate.html
│   └── ...
├── uploads/                    # Temporary uploaded images
├── face_auth.db               # SQLite database (created on first run)
├── aes.key                    # AES encryption key (created on first run)
├── requirements.txt           # Python dependencies
└── TROUBLESHOOTING.md         # Detailed troubleshooting guide
```

---

## Security Notes

1. **Change default admin password** immediately in production
2. **Use HTTPS** in production (set `app.config['PREFERRED_URL_SCHEME']`)
3. **Backup `aes.key`** - losing it means losing access to stored templates
4. **Use secure `SECRET_KEY`** in production (change in `src/config.py`)
5. **Face templates are encrypted** at rest with both:
   - Homomorphic Encryption (for computation without decryption)
   - AES encryption (for storage)

---

## Support

For detailed troubleshooting, see: **TROUBLESHOOTING.md**  
For summary of fixes applied: **FIXES_SUMMARY.py**
