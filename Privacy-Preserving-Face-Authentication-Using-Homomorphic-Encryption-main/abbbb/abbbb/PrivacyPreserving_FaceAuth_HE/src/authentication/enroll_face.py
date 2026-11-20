"""Face enrollment system"""
import numpy as np
from src.database.db_manager import create_user
from src.database.store_templates import TemplateStorage
from src.face_detection.detect_face import detect_face_in_image, encrypt_embedding
from cryptography.fernet import Fernet
import os
import pickle

class FaceEnrollment:
    """Handles user face enrollment with encryption"""
    
    def __init__(self, he_context=None):
        self.he_context = he_context
        # Initialize AES encryption
        self.cipher = self._init_cipher()
    
    def _init_cipher(self):
        """Initialize Fernet cipher for AES encryption"""
        key_file = "aes.key"
        if not os.path.exists(key_file):
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
        
        with open(key_file, "rb") as f:
            key = f.read()
        
        return Fernet(key)
    
    def enroll_user(self, username, image_path, full_name=None, email=None):
        """Enroll user with face image"""
        try:
            # Detect face and extract embedding using DeepFace
            face_detected, embedding = detect_face_in_image(image_path)
            
            if not face_detected:
                return False, "No face detected in the image. Please try again with a clear face photo."
            
            if embedding is None:
                return False, "Failed to extract face features. Please try again."
            
            # Create user in database
            print(f"[DEBUG] Attempting to create user: {username}")
            user_id = create_user(username, full_name, email)
            
            if not user_id:
                print(f"[ERROR] Failed to create user {username} - user_id is None")
                return False, "Failed to create user account. Username might already exist or a database error occurred."
            
            # Encrypt embedding using homomorphic encryption
            encrypted_embedding = encrypt_embedding(embedding, self.he_context)
            
            # Serialize encrypted embedding for storage
            # Always use pickle for consistency - it preserves shape and type information
            encrypted_bytes = pickle.dumps(encrypted_embedding)
            print(f"[DEBUG] Serialized embedding: type={type(encrypted_embedding)}, pickle size={len(encrypted_bytes)} bytes")
            
            # Also apply AES encryption for additional security
            final_encrypted = self.cipher.encrypt(encrypted_bytes)
            
            # Store the face template
            template_storage = TemplateStorage()
            template_storage.store_template(user_id, final_encrypted)
            
            message = f"User {username} enrolled"
            if full_name:
                message += f" (Name: {full_name})"
            if email:
                message += f" (Email: {email})"
            message += " with homomorphically encrypted face template!"
            
            return True, message
        
        except Exception as e:
            print(f"Enrollment error: {e}")
            return False, f"Enrollment failed: {str(e)}"
