import firebase_admin

from firebase_admin import credentials
from firebase_admin import auth

from pathlib import Path


# ============================================================
# FIREBASE ADMIN INITIALIZATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

CREDENTIALS_PATH = BASE_DIR / "firebase-admin.json"


if not firebase_admin._apps:

    cred = credentials.Certificate(
        CREDENTIALS_PATH
    )

    firebase_admin.initialize_app(
        cred
    )


# ============================================================
# VERIFY FIREBASE ID TOKEN
# ============================================================

def verify_token(id_token: str):

    """
    Verify a Firebase ID token and return
    the authenticated user's information.
    """

    decoded_token = auth.verify_id_token(
        id_token
    )

    return decoded_token