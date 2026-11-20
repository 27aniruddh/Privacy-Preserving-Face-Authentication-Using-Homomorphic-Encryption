# Privacy-Preserving AI-Based Biometric Authentication Using Homomorphic Encryption

A secure face authentication system that uses homomorphic encryption to protect biometric data. The system **only accepts images containing human faces** and performs all matching operations on encrypted data, ensuring complete privacy.

## 🔐 Key Features

- **Face Detection**: Automatically validates uploaded images contain human faces
- **Homomorphic Encryption**: Face templates encrypted using CKKS scheme from TenSEAL
- **Privacy-Preserving**: All biometric data stored and matched in encrypted form
- **Web Interface**: User-friendly Flask application with image upload
- **Admin Dashboard**: Complete admin control panel for user management
- **Secure Database**: SQLite database with encrypted face templates
- **Authentication Logs**: Comprehensive logging of all authentication attempts

## 📁 Project Structure

```
PrivacyPreserving_FaceAuth_HE/
│
├── dataset/
│   ├── enrollment_faces/          # Registered user face images
│   ├── auth_faces/                # Authentication test images
│   └── rejected_faces/            # Invalid/non-face images
│
├── src/
│   ├── config.py                  # Configuration settings
│   │
│   ├── face_detection/
│   │   ├── detect_face.py         # Face detection (Haar + DNN)
│   │   └── crop_face.py           # Face cropping and alignment
│   │
│   ├── preprocessing/
│   │   ├── normalize_face.py      # Face normalization
│   │   └── validate_image.py      # Image validation (ONLY accepts faces)
│   │
│   ├── feature_extraction/
│   │   ├── load_model.py          # CNN model loading
│   │   └── extract_embedding.py   # Face embedding extraction
│   │
│   ├── encryption/
│   │   ├── he_context.py          # CKKS encryption context
│   │   ├── encrypt_features.py    # Encrypt face embeddings
│   │   └── encrypted_distance.py  # Similarity on encrypted data
│   │
│   ├── database/
│   │   ├── db_manager.py          # Database operations
│   │   └── store_templates.py     # Template storage
│   │
│   └── authentication/
│       ├── enroll_face.py         # User enrollment
│       └── authenticate_face.py   # Face authentication
│
├── templates/                      # HTML templates
│   ├── base.html                  # Base template
│   ├── index.html                 # Home page
│   ├── enroll.html                # Enrollment page
│   ├── authenticate.html          # Authentication page
│   ├── admin_dashboard.html       # Admin dashboard
│   ├── admin_users.html           # User management
│   └── admin_logs.html            # Authentication logs
│
├── app.py                         # Flask web application
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 🚀 Installation

### 1. Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### 2. Install Dependencies

```bash
# Navigate to project directory
cd PrivacyPreserving_FaceAuth_HE

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 3. Verify Installation

```bash
python -c "import tenseal; import cv2; import tensorflow; print('✓ All dependencies installed')"
```

## 🎯 Usage

### Starting the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Default Admin Credentials

- **Username**: `admin`
- **Password**: `admin123`

⚠️ **IMPORTANT**: Change these credentials in production!

### User Enrollment

1. Navigate to **Enroll** page
2. Enter username and optional details
3. **Upload a clear face image** (ONLY images with faces are accepted)
4. System validates face presence automatically
5. If valid, user is enrolled with encrypted template

### User Authentication

1. Navigate to **Login** page
2. Choose authentication mode:
   - **Search All Users**: System finds matching user
   - **Specific Username**: Authenticate as specific user
3. Upload face image
4. System validates face and performs encrypted matching

### Admin Dashboard

1. Navigate to **Admin** and login
2. **Dashboard**: View statistics and recent activity
3. **User Management**: 
   - View all users
   - Activate/Deactivate users
   - Delete users permanently
4. **Authentication Logs**: View all authentication attempts

## 🔬 Technical Details

### Face Detection

- **Haar Cascade**: Fast detection for basic scenarios
- **DNN Model**: More accurate deep learning-based detection
- **Validation**: Only images with detected faces are accepted

### Feature Extraction

- CNN-based face embedding extraction
- 128-dimensional feature vectors
- L2 normalized embeddings

### Homomorphic Encryption

- **Scheme**: CKKS (Cheon-Kim-Kim-Song)
- **Library**: TenSEAL
- **Security**: Encrypted templates never decrypted during matching
- **Operations**: Euclidean distance computed on encrypted data

### Database Schema

**Users Table**:
- user_id, username, full_name, email
- created_at, last_login, is_active

**Face Templates Table**:
- template_id, user_id
- encrypted_embedding (BLOB)
- created_at, is_active

**Authentication Logs**:
- log_id, user_id, username
- auth_result, similarity_score, timestamp

## 📊 Configuration

Edit [src/config.py](src/config.py) to customize:

- **Similarity Threshold**: Adjust authentication threshold (0.0 - 1.0)
- **Encryption Parameters**: CKKS parameters for security/performance
- **File Upload**: Max file size, allowed extensions
- **Admin Credentials**: Default admin username/password

## 🛡️ Security Features

1. **Privacy-Preserving**: Biometric data always encrypted
2. **Face Validation**: Only accepts images with human faces
3. **Secure Storage**: No plaintext biometric data stored
4. **Admin Control**: Full user management capabilities
5. **Audit Logs**: Complete authentication history

## 🧪 Testing Individual Modules

### Test Face Detection

```bash
python src/face_detection/detect_face.py path/to/image.jpg
```

### Test Face Enrollment

```bash
python src/authentication/enroll_face.py username path/to/face.jpg "Full Name"
```

### Test Authentication

```bash
python src/authentication/authenticate_face.py path/to/face.jpg username
```

### Test Encryption

```bash
python src/encryption/he_context.py
```

## 📝 API Endpoints

### Public Endpoints

- `GET /` - Home page
- `GET /enroll` - Enrollment form
- `POST /enroll` - Submit enrollment
- `GET /authenticate` - Authentication form
- `POST /authenticate` - Submit authentication

### Admin Endpoints

- `GET /admin/login` - Admin login
- `GET /admin/dashboard` - Admin dashboard (protected)
- `GET /admin/users` - User management (protected)
- `POST /admin/user/<id>/toggle` - Toggle user status
- `POST /admin/user/<id>/delete` - Delete user
- `GET /admin/logs` - Authentication logs

### API Endpoints

- `POST /api/validate_image` - Validate if image contains face

## ⚠️ Important Notes

1. **Face Requirement**: System **ONLY accepts images with detected human faces**
2. **Image Quality**: Use clear, well-lit face images for best results
3. **Security**: Change default admin credentials in production
4. **Performance**: First run may be slower due to model loading
5. **Encryption**: CKKS parameters affect security and performance

## 🔧 Troubleshooting

### "No face detected" Error
- Ensure image contains a clear, frontal face
- Check lighting conditions
- Try a different image

### TenSEAL Installation Issues
```bash
pip install tenseal --no-binary tenseal
```

### OpenCV Issues
```bash
pip install opencv-python-headless
```

### Model Loading Errors
- Model downloads automatically on first run
- Check internet connection
- Verify TensorFlow installation

## 📚 Dependencies

- **Flask**: Web framework
- **TensorFlow**: Deep learning models
- **OpenCV**: Computer vision operations
- **TenSEAL**: Homomorphic encryption
- **NumPy**: Numerical operations
- **SQLite**: Database (built-in)

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

1. Enhanced face detection models
2. Multi-factor authentication
3. API documentation
4. Performance optimizations
5. Additional encryption schemes

## 📄 License

This project is for educational and research purposes.

## 🎓 Research Background

This system implements privacy-preserving biometric authentication using:

- **Homomorphic Encryption**: CKKS scheme for encrypted computations
- **Deep Learning**: CNN-based face recognition
- **Secure Multi-party Computation**: Template matching without decryption

## 👥 Admin Features

### User Management
- View all registered users
- Activate/Deactivate user accounts
- Delete users and their templates
- Monitor template counts

### Authentication Monitoring
- Real-time authentication logs
- Success/failure tracking
- Similarity scores
- IP address logging

### Statistics Dashboard
- Total users count
- Active/inactive users
- Recent login activity
- System health metrics

## 🔐 Privacy Guarantees

1. **No Plaintext Storage**: Biometric templates never stored in plaintext
2. **Encrypted Matching**: All comparisons on encrypted data
3. **Face-Only Policy**: Non-face images automatically rejected
4. **Secure Templates**: Homomorphic encryption ensures privacy
5. **Audit Trail**: Complete logging for security analysis

## 📞 Support

For issues or questions:
1. Check this README
2. Review code comments
3. Test individual modules
4. Check authentication logs in admin panel

---

**Built with privacy and security in mind** 🔐
