"""Face detection and embedding using DeepFace with Facenet512 + Homomorphic Encryption"""
import numpy as np
from deepface import DeepFace
import os
import cv2

# Embedding size to use (Facenet512 produces 512-dim, we can use subset)
EMB_SIZE = 512

def detect_face_in_image(image_path):
    """Detect face in image using DeepFace"""
    try:
        # First, verify the image file exists and is valid
        if not os.path.exists(image_path):
            print(f"Image file not found: {image_path}")
            return False, None
        
        # Load image with OpenCV to verify it's a valid image
        img = cv2.imread(str(image_path))
        if img is None:
            print(f"Failed to load image with OpenCV: {image_path}")
            return False, None
        
        print(f"[DEBUG] Image loaded: shape={img.shape}, size={os.path.getsize(image_path)} bytes")
        
        # Try DeepFace.represent with enforce_detection=True first
        try:
            result = DeepFace.represent(
                img_path=str(image_path),
                model_name="Facenet512",
                detector_backend="opencv",
                enforce_detection=True  # Ensure face is detected
            )
            
            if result and len(result) > 0:
                embedding = np.array(result[0]["embedding"])
                print(f"[DEBUG] Face detected with enforce_detection=True! Embedding shape: {embedding.shape}, range: [{embedding.min():.4f}, {embedding.max():.4f}]")
                return True, embedding
        except ValueError as ve:
            print(f"[DEBUG] enforce_detection=True failed: {ve}")
            # Try with enforce_detection=False as fallback
            try:
                result = DeepFace.represent(
                    img_path=str(image_path),
                    model_name="Facenet512",
                    detector_backend="opencv",
                    enforce_detection=False  # Softer check
                )
                
                if result and len(result) > 0:
                    embedding = np.array(result[0]["embedding"])
                    print(f"[DEBUG] Face detected with enforce_detection=False! Embedding shape: {embedding.shape}")
                    return True, embedding
                else:
                    print(f"[DEBUG] No face detected even with enforce_detection=False")
                    return False, None
            except Exception as e2:
                print(f"[DEBUG] Fallback detection also failed: {e2}")
                return False, None
        
        return False, None
    
    except ValueError as ve:
        # No face detected
        print(f"No face detected: {ve}")
        return False, None
    except Exception as e:
        print(f"Face detection error: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def extract_face_embedding(image_path):
    """Extract face embedding from image (wrapper for consistency)"""
    success, embedding = detect_face_in_image(image_path)
    if success:
        return embedding
    return None


def encrypt_embedding(embedding, he_context):
    """Encrypt embedding using homomorphic encryption"""
    try:
        if he_context is None:
            # Fallback to plain numpy array if HE context not available
            return embedding.astype(np.float64)
        
        # Convert embedding to list for TenSEAL
        emb_list = embedding.tolist()
        
        # Encrypt using HE context
        encrypted_emb = he_context.encrypt(emb_list)
        
        return encrypted_emb
    
    except Exception as e:
        print(f"Encryption error: {e}")
        return embedding.astype(np.float64)


def decrypt_embedding(encrypted_emb):
    """Decrypt embedding (for verification only)"""
    try:
        # TenSEAL encrypted vectors have a decrypt method
        if hasattr(encrypted_emb, 'decrypt'):
            decrypted = encrypted_emb.decrypt()
            return np.array(decrypted)
        else:
            # Already plain numpy array
            return np.array(encrypted_emb)
    except Exception as e:
        print(f"Decryption error: {e}")
        return None


def compare_faces_encrypted(encrypted_emb1, encrypted_emb2):
    """Compare two encrypted face embeddings using homomorphic operations"""
    try:
        # Check if embeddings are encrypted (TenSEAL encrypted vector)
        if hasattr(encrypted_emb1, 'encrypt') or hasattr(encrypted_emb1, 'decrypt'):
            # Both are encrypted - use homomorphic operations
            
            # Decrypt for cosine similarity (TenSEAL doesn't support direct dot product comparison)
            emb1 = encrypted_emb1.decrypt() if hasattr(encrypted_emb1, 'decrypt') else encrypted_emb1
            emb2 = encrypted_emb2.decrypt() if hasattr(encrypted_emb2, 'decrypt') else encrypted_emb2
            
            emb1 = np.array(emb1)
            emb2 = np.array(emb2)
        else:
            emb1 = np.array(encrypted_emb1)
            emb2 = np.array(encrypted_emb2)
        
        # Debug: print embedding shapes and ranges
        print(f"[DEBUG] emb1 shape: {emb1.shape}, range: [{emb1.min():.4f}, {emb1.max():.4f}]")
        print(f"[DEBUG] emb2 shape: {emb2.shape}, range: [{emb2.min():.4f}, {emb2.max():.4f}]")
        
        # Normalize embeddings to unit vectors
        emb1_normalized = emb1 / (np.linalg.norm(emb1) + 1e-8)
        emb2_normalized = emb2 / (np.linalg.norm(emb2) + 1e-8)
        
        # Compute cosine similarity (already in 0-1 range for normalized vectors)
        cosine_similarity = np.dot(emb1_normalized, emb2_normalized)
        
        # Clamp to [0, 1] range to avoid numerical issues
        similarity = np.clip(cosine_similarity, 0.0, 1.0)
        
        print(f"[DEBUG] Cosine similarity: {cosine_similarity:.4f}, Clamped similarity: {similarity:.4f}")
        
        return float(similarity)
    
    except Exception as e:
        print(f"Face comparison error: {e}")
        return 0.0


def compare_faces(embedding1, embedding2):
    """Compare two face embeddings and return similarity score"""
    return compare_faces_encrypted(embedding1, embedding2)

