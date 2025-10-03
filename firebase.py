import os
import json
import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv

load_dotenv()

def initialize_firebase():
    if firebase_admin._apps:
        return

    firebase_json_str = os.getenv("FIREBASE_JSON_STRING")

    if not firebase_json_str:
        raise ValueError(
            "FIREBASE_JSON_STRING not found in environment variables. "
            "Please ensure your .env file contains the Firebase service account credentials."
        )

    try:
        firebase_credentials = json.loads(firebase_json_str)
        cred = credentials.Certificate(firebase_credentials)
        firebase_admin.initialize_app(cred)
        print("Firebase Admin SDK initialized successfully")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in FIREBASE_JSON_STRING: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to initialize Firebase: {str(e)}")

initialize_firebase()