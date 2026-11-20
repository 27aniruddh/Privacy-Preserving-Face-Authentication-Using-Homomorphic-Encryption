"""Face authentication system"""
import numpy as np
from src.database.db_manager import get_user_by_username, get_connection
from src.database.store_templates import TemplateStorage
from src.face_detection.detect_face import detect_face_in_image, encrypt_embedding, compare_faces
from src.config import AUTHENTICATION_THRESHOLD, PRE_ENROLLMENT_THRESHOLD, SKIP_DUPLICATE_CHECK
from cryptography.fernet import Fernet
import os
import pickle

class FaceAuthentication:
    """Handles face-based authentication with homomorphic encryption"""
    
    def __init__(self, he_context=None):
        self.he_context = he_context
        # Initialize AES encryption
        self.cipher = self._init_cipher()
    
    def _init_cipher(self):
        """Initialize Fernet cipher for AES decryption"""
        key_file = "aes.key"
        if not os.path.exists(key_file):
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
        
        with open(key_file, "rb") as f:
            key = f.read()
        
        return Fernet(key)
    
    def _deserialize_embedding(self, encrypted_bytes):
        """Deserialize encrypted embedding from storage"""
        try:
            # Everything is stored as pickle for consistency
            embedding = pickle.loads(encrypted_bytes)
            print(f"[DEBUG] Deserialized embedding: type={type(embedding)}")
            
            # If it's a numpy array, verify it
            if isinstance(embedding, np.ndarray):
                print(f"[DEBUG] Embedding is numpy array, shape: {embedding.shape}, dtype: {embedding.dtype}")
            
            return embedding
        except Exception as e:
            print(f"[DEBUG] Failed to deserialize: {e}")
            return None
    
    def authenticate(self, image_path, username=None):
        """Authenticate user with face image using homomorphic encryption"""
        try:
            # Detect face and extract embedding using DeepFace
            face_detected, embedding = detect_face_in_image(image_path)
            
            if not face_detected:
                return False, {"message": "No face detected in the image. Please try again."}
            
            if embedding is None:
                return False, {"message": "Failed to extract face features. Please try again."}
            
            # Encrypt the authentication embedding using HE
            auth_encrypted = encrypt_embedding(embedding, self.he_context)
            
            template_storage = TemplateStorage()
            
            # If username provided, authenticate against specific user
            if username:
                user = get_user_by_username(username)
                if not user:
                    return False, {"message": f"User {username} not found."}
                
                user_id = user[0]
                
                # Retrieve stored encrypted template
                stored_encrypted = template_storage.retrieve_template(user_id)
                
                if not stored_encrypted:
                    return False, {"message": f"No face template found for {username}."}
                
                # Decrypt AES layer
                decrypted_aes = self.cipher.decrypt(stored_encrypted)
                stored_embedding = self._deserialize_embedding(decrypted_aes)
                
                if stored_embedding is None:
                    return False, {"message": "Failed to load stored template."}
                
                # Compare embeddings (homomorphically encrypted if HE is enabled)
                similarity = compare_faces(auth_encrypted, stored_embedding)
                
                if similarity >= AUTHENTICATION_THRESHOLD:
                    result = {
                        "username": username,
                        "similarity_score": round(similarity, 4),
                        "message": f"[OK] Authentication successful for {username}!"
                    }
                    return True, result
                else:
                    return False, {
                        "message": f"Face does not match {username}. Similarity: {round(similarity, 4)}"
                    }
            
            # If no username provided, search all users
            else:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT id, username FROM users WHERE is_active = 1")
                users = cursor.fetchall()
                conn.close()
                
                if not users:
                    return False, {"message": "No registered users found."}
                
                best_match = None
                best_score = 0.0
                
                # Compare against all users
                for user_id, user_name in users:
                    stored_encrypted = template_storage.retrieve_template(user_id)
                    
                    if stored_encrypted:
                        # Decrypt AES layer
                        decrypted_aes = self.cipher.decrypt(stored_encrypted)
                        stored_embedding = self._deserialize_embedding(decrypted_aes)
                        
                        if stored_embedding is not None:
                            similarity = compare_faces(auth_encrypted, stored_embedding)
                            print(f"[DEBUG] User {user_name}: similarity = {similarity:.4f}")
                            
                            if similarity > best_score:
                                best_score = similarity
                                best_match = user_name
                
                print(f"[DEBUG] Best match: {best_match} with score {best_score:.4f}, threshold: {AUTHENTICATION_THRESHOLD}")
                
                if best_score >= AUTHENTICATION_THRESHOLD:
                    result = {
                        "username": best_match,
                        "similarity_score": round(best_score, 4),
                        "message": f"[OK] Authentication successful! Welcome, {best_match}!"
                    }
                    return True, result
                else:
                    return False, {
                        "message": f"Face not recognized. Best match score: {round(best_score, 4)}"
                    }
        
        except Exception as e:
            print(f"Authentication error: {e}")
            return False, {"message": f"Authentication failed: {str(e)}"}

    def find_existing_user_by_face(self, image_path):
        """Check if a face is already enrolled. Returns (matched, info, error_message)."""
        try:
            # If duplicate check is disabled, allow all enrollments (for testing)
            if SKIP_DUPLICATE_CHECK:
                print("[INFO] Pre-enrollment duplicate check DISABLED - allowing all enrollments")
                return False, None, None
            
            face_detected, embedding = detect_face_in_image(image_path)

            if not face_detected or embedding is None:
                return False, None, "Face is not properly visible. Please try again with a clear face image."

            auth_encrypted = encrypt_embedding(embedding, self.he_context)
            template_storage = TemplateStorage()

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, username FROM users WHERE is_active = 1")
            users = cursor.fetchall()
            conn.close()

            best_match = None
            best_score = 0.0

            for user_id, user_name in users:
                stored_encrypted = template_storage.retrieve_template(user_id)
                if stored_encrypted:
                    decrypted_aes = self.cipher.decrypt(stored_encrypted)
                    stored_embedding = self._deserialize_embedding(decrypted_aes)
                    if stored_embedding is None:
                        print(f"[DEBUG] Could not deserialize embedding for {user_name}")
                        continue

                    similarity = compare_faces(auth_encrypted, stored_embedding)
                    print(f"[DEBUG] Pre-enroll check - User {user_name}: similarity = {similarity:.4f}")
                    if similarity > best_score:
                        best_score = similarity
                        best_match = user_name

            print(f"[DEBUG] Pre-enroll best match: {best_match} with score {best_score:.4f}, threshold: {PRE_ENROLLMENT_THRESHOLD}")
            
            # Only flag as duplicate if EXTREMELY similar (99%+)
            if best_match and best_score >= PRE_ENROLLMENT_THRESHOLD:
                print(f"[WARNING] Pre-enroll BLOCKED: Extremely high match to {best_match} with score {best_score:.4f}")
                return True, {
                    "username": best_match,
                    "similarity_score": round(best_score, 4)
                }, None
            else:
                # Allow enrollment as new user
                if best_match:
                    print(f"[INFO] Pre-enroll ALLOWED: Best match to {best_match} only {best_score:.4f} (below {PRE_ENROLLMENT_THRESHOLD} threshold)")
                else:
                    print(f"[INFO] Pre-enroll ALLOWED: No existing users to match against")
                return False, None, None

        except Exception as e:
            print(f"Pre-enrollment check error: {e}")
            return False, None, f"Pre-enrollment check failed: {str(e)}"

