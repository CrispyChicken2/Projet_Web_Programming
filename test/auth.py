import base64
import hashlib
import hmac
import secrets

from models import User


PBKDF2_ITERATIONS = 260_000


def hash_password(password: str) -> str:
    """Transforme un mot de passe en hash stockable en base."""
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )

    salt_text = base64.b64encode(salt).decode("ascii")
    hash_text = base64.b64encode(password_hash).decode("ascii")
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt_text}${hash_text}"


def verify_password(password: str, stored_password_hash: str) -> bool:
    """Compare un mot de passe saisi avec le hash sauvegarde."""
    try:
        algorithm, iterations, salt_text, hash_text = stored_password_hash.split("$")
        if algorithm != "pbkdf2_sha256":
            return False

        salt = base64.b64decode(salt_text.encode("ascii"))
        expected_hash = base64.b64decode(hash_text.encode("ascii"))
        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            int(iterations),
        )
        return hmac.compare_digest(password_hash, expected_hash)
    except (ValueError, TypeError):
        return False


def get_current_user(request, db):
    """Retourne l'utilisateur connecte grace a l'identifiant en session."""
    user_id = request.session.get("user_id")
    if user_id is None:
        return None

    return db.query(User).filter(User.id == user_id).first()


def login_user(request, user: User):
    """Enregistre l'identifiant utilisateur dans la session."""
    request.session["user_id"] = user.id


def logout_user(request):
    """Vide la session de l'utilisateur."""
    request.session.clear()
