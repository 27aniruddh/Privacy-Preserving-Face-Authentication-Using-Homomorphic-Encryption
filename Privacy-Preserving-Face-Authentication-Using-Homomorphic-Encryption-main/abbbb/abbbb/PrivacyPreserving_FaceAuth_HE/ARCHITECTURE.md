# System Architecture

## Privacy-Preserving Face Authentication System

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     USER INTERFACE (Web)                      │
├──────────────────────────────────────────────────────────────┤
│  Home  │  Enroll  │  Authenticate  │  Admin Dashboard        │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                   FLASK APPLICATION (app.py)                  │
├──────────────────────────────────────────────────────────────┤
│  • Route Handling                                             │
│  • File Upload Management                                     │
│  • Session Management                                         │
│  • Admin Authentication                                       │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                    CORE MODULES (src/)                        │
└──────────────────────────────────────────────────────────────┘

┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Face Detection  │  │ Preprocessing   │  │ Validation      │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ • Haar Cascade  │  │ • Normalization │  │ • Face Check ✓  │
│ • DNN Detector  │  │ • Resizing      │  │ • Quality Check │
│ • Face Crop     │  │ • Enhancement   │  │ • Format Check  │
└─────────────────┘  └─────────────────┘  └─────────────────┘
        │                     │                     │
        └─────────────────────┴─────────────────────┘
                            │
                            ▼
                ┌─────────────────────────┐
                │  Feature Extraction     │
                ├─────────────────────────┤
                │  • CNN Model            │
                │  • 128D Embeddings      │
                │  • L2 Normalization     │
                └─────────────────────────┘
                            │
                            ▼
                ┌─────────────────────────┐
                │ Homomorphic Encryption  │
                ├─────────────────────────┤
                │  • CKKS Context         │
                │  • Encrypt Embeddings   │
                │  • Encrypted Distance   │
                └─────────────────────────┘
                            │
                            ▼
                ┌─────────────────────────┐
                │  Database (SQLite)      │
                ├─────────────────────────┤
                │  • Users Table          │
                │  • Templates (Encrypted)│
                │  • Auth Logs            │
                │  • Admin Users          │
                └─────────────────────────┘
```

### Enrollment Flow

```
User uploads image
      │
      ▼
┌──────────────┐
│ Validate     │ ──NO──► Reject Image
│ Face Present │         (Return Error)
└──────────────┘
      │ YES
      ▼
┌──────────────┐
│ Detect Face  │
│ & Crop       │
└──────────────┘
      │
      ▼
┌──────────────┐
│ Extract      │
│ 128D         │
│ Embedding    │
└──────────────┘
      │
      ▼
┌──────────────┐
│ Encrypt with │
│ CKKS         │
└──────────────┘
      │
      ▼
┌──────────────┐
│ Store in DB  │
│ (Encrypted)  │
└──────────────┘
      │
      ▼
 Enrollment Success!
```

### Authentication Flow

```
User uploads image
      │
      ▼
┌──────────────┐
│ Validate     │ ──NO──► Reject Image
│ Face Present │         (Return Error)
└──────────────┘
      │ YES
      ▼
┌──────────────┐
│ Extract      │
│ Probe        │
│ Embedding    │
└──────────────┘
      │
      ▼
┌──────────────┐
│ Encrypt      │
│ Probe        │
└──────────────┘
      │
      ▼
┌──────────────────────┐
│ Load All Encrypted   │
│ Templates from DB    │
└──────────────────────┘
      │
      ▼
┌──────────────────────┐
│ Compare on Encrypted │
│ Data (No Decryption) │
└──────────────────────┘
      │
      ▼
┌──────────────────────┐
│ Compute Similarity   │
│ Score                │
└──────────────────────┘
      │
      ▼
  Score >= Threshold?
      │
      ├──YES──► Authentication Success!
      │
      └──NO───► Authentication Failed
```

### Admin Dashboard Flow

```
Admin Login
      │
      ▼
┌──────────────────────┐
│ Verify Credentials   │
│ (Password Hash)      │
└──────────────────────┘
      │
      ▼
┌──────────────────────┐
│ Dashboard            │
├──────────────────────┤
│ • User Statistics    │
│ • Recent Logins      │
│ • System Health      │
└──────────────────────┘
      │
      ├──► User Management
      │    ├─ View Users
      │    ├─ Activate/Deactivate
      │    └─ Delete Users
      │
      └──► Authentication Logs
           ├─ View All Attempts
           ├─ Filter by Result
           └─ Export Data
```

### Database Schema

```
┌─────────────────────┐
│      USERS          │
├─────────────────────┤
│ user_id (PK)        │
│ username (UNIQUE)   │
│ full_name           │
│ email               │
│ created_at          │
│ last_login          │
│ is_active           │
│ failed_attempts     │
└─────────────────────┘
         │
         │ 1:N
         │
         ▼
┌─────────────────────┐
│   FACE_TEMPLATES    │
├─────────────────────┤
│ template_id (PK)    │
│ user_id (FK)        │
│ encrypted_embedding │ ◄── ENCRYPTED DATA
│ embedding_version   │
│ created_at          │
│ is_active           │
└─────────────────────┘

┌─────────────────────┐
│    AUTH_LOGS        │
├─────────────────────┤
│ log_id (PK)         │
│ user_id (FK)        │
│ username            │
│ auth_result         │
│ similarity_score    │
│ timestamp           │
│ ip_address          │
└─────────────────────┘

┌─────────────────────┐
│   ADMIN_USERS       │
├─────────────────────┤
│ admin_id (PK)       │
│ username (UNIQUE)   │
│ password_hash       │
│ created_at          │
│ last_login          │
└─────────────────────┘
```

### Security Layers

```
┌────────────────────────────────────────┐
│          Application Layer              │
│  • Session Management                   │
│  • CSRF Protection                      │
│  • File Upload Validation               │
└────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────┐
│        Face Validation Layer            │
│  • ONLY faces accepted ✓                │
│  • Quality checks                       │
│  • Format validation                    │
└────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────┐
│       Encryption Layer (CKKS)           │
│  • Homomorphic Encryption               │
│  • Secure Key Management                │
│  • Encrypted Computations               │
└────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────┐
│         Database Layer                  │
│  • Encrypted Templates Only             │
│  • Access Controls                      │
│  • Audit Logging                        │
└────────────────────────────────────────┘
```

### Technology Stack

```
┌─────────────────────────────────────────────┐
│              Frontend Layer                  │
│  HTML5 + CSS3 + JavaScript                  │
│  Responsive Design, Image Preview           │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│            Web Framework                     │
│  Flask 3.0 (Python)                         │
│  Werkzeug, Jinja2 Templates                 │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│          Computer Vision                     │
│  OpenCV 4.9 - Face Detection                │
│  Haar Cascade + DNN                         │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│          Deep Learning                       │
│  TensorFlow 2.15 - CNN Models               │
│  Face Embeddings (128D)                     │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│       Homomorphic Encryption                 │
│  TenSEAL - CKKS Scheme                      │
│  Encrypted Computations                     │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│             Database                         │
│  SQLite - Encrypted Templates               │
│  Users, Logs, Admin                         │
└─────────────────────────────────────────────┘
```

### Key Features Summary

```
✅ Face Detection       → Haar Cascade + DNN
✅ Face Validation      → ONLY faces accepted
✅ Feature Extraction   → 128D embeddings
✅ Encryption           → CKKS homomorphic
✅ Matching             → Encrypted domain
✅ Web Interface        → Flask application
✅ Admin Dashboard      → Full management
✅ Database             → SQLite storage
✅ Logging              → Complete audit trail
✅ Security             → Multi-layer protection
```

---

This architecture ensures:
- **Privacy**: All biometric data encrypted
- **Security**: Face validation prevents abuse
- **Usability**: User-friendly web interface
- **Scalability**: Modular design
- **Maintainability**: Clean code structure
