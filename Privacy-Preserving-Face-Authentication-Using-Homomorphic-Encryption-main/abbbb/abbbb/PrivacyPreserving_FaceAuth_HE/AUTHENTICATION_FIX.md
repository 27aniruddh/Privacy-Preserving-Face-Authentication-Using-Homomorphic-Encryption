# Authentication Issue - Root Cause Analysis and Fix

## Problem Description
When uploading the same image used during enrollment for authentication, the system was failing to recognize the face, even though it should match perfectly (similarity ~1.0).

## Root Cause
The issue was caused by **different Homomorphic Encryption (HE) contexts being created** for enrollment and authentication:

1. **During Enrollment**: A new HE context was created with specific encryption keys
   - Face embedding was extracted and encrypted with these keys
   - Encrypted template was stored in database

2. **During Authentication**: A different HE context was created with different encryption keys
   - Probe embedding was extracted and encrypted with these NEW keys
   - When comparing: encrypted values were completely different despite identical embeddings
   - Result: Low similarity score, authentication failed

### Why This Happened
- `FaceEnrollment.__init__()` called `create_he_context()` → created new context with unique keys
- `FaceAuthentication.__init__()` called `create_he_context()` → created another new context with different keys
- Different encryption keys = different ciphertexts for the same plaintext values
- Comparison failed despite embeddings being identical

## Solution Implemented
Implemented a **shared, persistent HE context** across the entire application:

### Changes Made

#### 1. Updated `src/authentication/enroll_face.py`
- Added `get_shared_he_context()` function that uses global singleton pattern
- Changed `FaceEnrollment.__init__()` to use shared context
- Changed type hint from `HEContext` to `ts.Context`

#### 2. Updated `src/authentication/authenticate_face.py`
- Added `get_shared_he_context()` function that uses global singleton pattern
- Changed `FaceAuthentication.__init__()` to use shared context
- Changed type hint from `HEContext` to `ts.Context`

#### 3. Updated `app.py`
- Initialize shared HE context **once** when Flask app starts
- Pass the same context instance to both `FaceEnrollment` and `FaceAuthentication`
- This ensures all enrollments and authentications use the same encryption keys

### How It Works Now
```python
# app.py - Initialization
shared_he_context = get_global_context()  # Create once at startup

# Both systems now use the SAME context
enrollment_system = FaceEnrollment(shared_he_context)
auth_system = FaceAuthentication(shared_he_context)

# Result:
# - Enrollment: face → embedding → encrypt with KEY_A → store
# - Authentication: face → embedding → encrypt with KEY_A → compare
# - Since both use KEY_A, encrypted values match for identical embeddings
```

## Expected Behavior After Fix
- Upload same image during enrollment: ✓ Success (~0.99 similarity)
- Upload same image during authentication: ✓ Success (~0.99 similarity)
- Upload different faces: ✓ Correctly rejected (low similarity)

## Testing the Fix
1. Start the Flask app: `python app.py`
2. Enroll a user with a face image
3. Authenticate with the **exact same image**
4. Result should show: **Authentication successful** with high similarity score (>0.9)

## Technical Notes
- The fix uses Python's global singleton pattern to ensure only one HE context per application lifecycle
- HE contexts are expensive to create, so reusing them also improves performance
- The context includes all necessary encryption keys needed for both encryption and decryption operations
