import firebase_admin
from firebase_admin import credentials, firestore, storage
from typing import Optional, Dict, Any
from app.config import settings
from app.utils.logger import logger
import json
import os

class FirebaseClient:
    """Firebase connection manager."""
    
    _instance = None
    _db = None
    _storage = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not firebase_admin._apps:
            self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK."""
        try:
            if settings.FIREBASE_CREDENTIALS_PATH and os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            else:
                cred_dict = {
                    "type": "service_account",
                    "project_id": settings.FIREBASE_PROJECT_ID,
                    "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
                    "private_key": settings.FIREBASE_PRIVATE_KEY.replace("\\n", "\n") if settings.FIREBASE_PRIVATE_KEY else None,
                    "client_email": settings.FIREBASE_CLIENT_EMAIL,
                    "client_id": settings.FIREBASE_CLIENT_ID,
                    "auth_uri": settings.FIREBASE_AUTH_URI,
                    "token_uri": settings.FIREBASE_TOKEN_URI,
                }
                cred = credentials.Certificate(cred_dict)
            
            firebase_admin.initialize_app(cred, {
                'projectId': settings.FIREBASE_PROJECT_ID,
            })
            
            self._db = firestore.client()
            self._storage = storage.bucket(f"{settings.FIREBASE_PROJECT_ID}.appspot.com")
            
            logger.info("Firebase initialized successfully", extra={"project_id": settings.FIREBASE_PROJECT_ID})
        except Exception as e:
            logger.error(f"Firebase initialization failed: {str(e)}")
            raise
    
    @property
    def db(self):
        """Get Firestore database instance."""
        if self._db is None:
            self._initialize_firebase()
        return self._db
    
    @property
    def storage(self):
        """Get Storage bucket instance."""
        if self._storage is None:
            self._initialize_firebase()
        return self._storage

firebase_client = FirebaseClient()
