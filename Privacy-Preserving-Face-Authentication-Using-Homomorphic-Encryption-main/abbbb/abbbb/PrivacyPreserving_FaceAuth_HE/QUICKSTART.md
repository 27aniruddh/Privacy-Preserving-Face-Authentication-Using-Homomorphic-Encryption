# Quick Start Guide

## Privacy-Preserving Face Authentication System

### Installation Steps

1. **Install Python Dependencies**
```bash
cd PrivacyPreserving_FaceAuth_HE
pip install -r requirements.txt
```

2. **Run the Application**
```bash
python app.py
```

3. **Access the Web Interface**
- Open browser: http://localhost:5000
- Default admin credentials:
  - Username: `admin`
  - Password: `admin123`

### Quick Test

1. **Enroll a User**
   - Go to "Enroll" page
   - Enter username: `test_user`
   - Upload a face image (must contain a visible face!)
   - Click "Enroll User"

2. **Authenticate**
   - Go to "Login" page
   - Select "Specific Username"
   - Enter username: `test_user`
   - Upload the same or similar face image
   - Click "Authenticate"

3. **Admin Panel**
   - Go to "Admin" page
   - Login with admin credentials
   - View users, manage accounts, check logs

### Important Notes

✅ **ONLY images containing human faces are accepted**
✅ Images are validated automatically
✅ Non-face images are rejected immediately
✅ All face data is encrypted with homomorphic encryption

### Troubleshooting

**Problem**: "No face detected"
- **Solution**: Use a clear face image with good lighting

**Problem**: TenSEAL installation error
- **Solution**: `pip install tenseal --no-binary tenseal`

**Problem**: Model loading takes time
- **Solution**: First run downloads models, be patient

**Problem**: OpenCV errors
- **Solution**: `pip install opencv-python-headless`

### Project Features

- 🔒 Homomorphic encryption for privacy
- 👤 Face detection validation
- 🎯 High accuracy authentication
- 👨‍💼 Admin dashboard for user management
- 📊 Complete authentication logging
- 🛡️ Secure encrypted template storage

### File Structure

```
PrivacyPreserving_FaceAuth_HE/
├── app.py                    # Main Flask application
├── src/                      # Source code modules
│   ├── config.py            # Configuration
│   ├── face_detection/      # Face detection
│   ├── preprocessing/       # Image validation
│   ├── feature_extraction/  # Embedding extraction
│   ├── encryption/          # Homomorphic encryption
│   ├── database/            # Database management
│   └── authentication/      # Enroll & authenticate
├── templates/               # HTML templates
├── dataset/                 # Face images
├── models/                  # ML models
└── outputs/                 # Results & logs
```

### Next Steps

1. Change admin password in [src/config.py](src/config.py)
2. Adjust similarity threshold if needed
3. Add your own face images for testing
4. Explore admin dashboard features
5. Check authentication logs

### Security Reminders

⚠️ Change default admin password
⚠️ Use HTTPS in production
⚠️ Regular backup of database
⚠️ Monitor authentication logs
⚠️ Only accept trusted image uploads

---

**Ready to start!** Run `python app.py` and visit http://localhost:5000
