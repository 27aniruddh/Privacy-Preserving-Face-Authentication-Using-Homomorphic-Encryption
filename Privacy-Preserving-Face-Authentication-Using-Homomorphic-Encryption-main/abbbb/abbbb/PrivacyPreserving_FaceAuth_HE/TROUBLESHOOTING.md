# Face Authentication System - Setup & Troubleshooting Guide

## Quick Start

### 1. Fresh Installation
```bash
# Clear any old data
rm face_auth.db
rm aes.key

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

The app will run on `http://localhost:5000`

---

## How It Works

### Face Embedding
- Uses **Facenet512** model to extract 512-dimensional face embeddings
- Different faces produce different embeddings
- Same person produces similar embeddings

### Similarity Thresholds
- **Pre-Enrollment (0.95)**: Very strict - blocks duplicate enrollments only if face is >95% similar
- **Authentication (0.85)**: Moderate - accepts face if >85% similar to enrolled face

### Expected Scores
- Different people: 0.60 - 0.80 similarity
- Same person (different photos): 0.85 - 1.00 similarity

---

## Usage Instructions

### Enrolling Users

1. Go to `/enroll`
2. Enter **unique** username (must be different from other enrolled users)
3. Optionally add full name and email
4. Capture face image via webcam (clear face, good lighting)
5. System will:
   - Detect if face is already enrolled (0.95 threshold = very strict)
   - Create user account if new
   - Store encrypted face template
6. Success: User is enrolled

**Important**: 
- Each username must be unique
- Different people WILL have different embeddings (no false blocking)
- Only exact duplicates (>95% match) are blocked

### Authenticating Users

1. Go to `/authenticate`
2. Optionally enter username (if not entered, searches all users)
3. Capture face image via webcam
4. System will:
   - Compare against enrolled templates (0.85 threshold)
   - Find best match across all users
   - Accept if score >= 0.85
5. Success: User details shown

### Admin Dashboard

1. Go to `/admin/login` (default: admin/admin123)
2. View all enrolled users
3. View authentication logs
4. Deactivate/delete users if needed

---

## Troubleshooting

### "Already enrolled as [other user]" when enrolling new person

**Cause**: Pre-enrollment check thinks new face matches existing user  
**Fix**: 
- Ensure good lighting and clear face
- Use different angle/position than existing user
- Check console logs for similarity score (should be < 0.95)

### Authentication shows wrong user details

**Cause**: Face similarity between users is too high (bad embeddings)  
**Fix**:
- Check quality of enrolled faces (must have good lighting)
- Make sure different users have clearly different faces
- Re-enroll with better quality images

### Console shows different similarity scores each time

**This is normal** - each authentication extracts embedding from fresh image  
- Same person: should be 0.9+
- Different person: should be 0.6-0.8

---

## Debug Output

Check console for logs like:
```
[DEBUG] Face detected! Embedding shape: (512,), range: [-0.21, 0.45]
[DEBUG] Pre-enroll check - User anirudh: similarity = 0.72
[DEBUG] Pre-enroll best match: anirudh with score 0.72, threshold: 0.95
[INFO] Pre-enroll ALLOWED: Best match to anirudh only 0.72 (below 0.95 threshold)
```

If similarity between different people is > 0.90, there's an issue with embedding extraction.

---

## Database Reset

If authentication is misbehaving:

```bash
# Stop the app
# Run:
rm face_auth.db
rm aes.key
# Then restart app - it will recreate database fresh
```

---

## Key Changes Made

1. **Fixed embedding serialization** - Using pickle instead of tobytes()
2. **Fixed similarity calculation** - Proper cosine similarity normalization  
3. **Stricter pre-enrollment threshold (0.95)** - Different people won't block each other
4. **Added comprehensive debug logging** - See what's happening
5. **Username validation** - Can't create duplicate usernames
6. **Email validation** - Must be valid email format

---

## Expected Behavior

✓ Person A enrolls successfully  
✓ Person B (different face) enrolls successfully (not blocked as "already enrolled")  
✓ Person A authenticates - shows Person A's details  
✓ Person B authenticates - shows Person B's details  
✓ Unknown face - "Face not recognized"  

If this is NOT happening, check console logs for similarity scores!
