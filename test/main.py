import json

from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from auth import (
    get_current_user,
    hash_password,
    login_user,
    logout_user,
    verify_password,
)
from database import create_database, get_db
from models import CV, User


app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key="change-this-secret-key-for-a-real-project",
)

# Dossiers utilises par FastAPI pour trouver les fichiers du projet.
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
def on_startup():
    """Prepare la base de donnees au lancement de l'application."""
    create_database()


@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    """Affiche le formulaire du CV de l'utilisateur connecte."""
    user = get_current_user(request, db)
    if user is None:
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)

    cv_record = db.query(CV).filter(CV.user_id == user.id).first()
    cv = cv_record_to_dict(cv_record, default_email=user.email)

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "request": request,
            "user": user,
            "cv": cv,
            "has_cv": cv_record is not None,
        },
    )


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request, db: Session = Depends(get_db)):
    """Affiche le formulaire d'inscription."""
    if get_current_user(request, db):
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        request,
        "register.html",
        {"request": request, "error": None, "email": ""},
    )


@app.post("/register", response_class=HTMLResponse)
async def register(request: Request, db: Session = Depends(get_db)):
    """Cree un compte utilisateur puis connecte directement l'utilisateur."""
    form = await request.form()
    email = form.get("email", "").strip().lower()
    password = form.get("password", "")

    if not email or not password:
        return auth_template(
            request,
            "register.html",
            "L'adresse email et le mot de passe sont obligatoires.",
            email,
        )

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return auth_template(
            request,
            "register.html",
            "Un compte existe deja avec cette adresse email.",
            email,
        )

    user = User(email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)

    login_user(request, user)
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request, db: Session = Depends(get_db)):
    """Affiche le formulaire de connexion."""
    if get_current_user(request, db):
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        request,
        "login.html",
        {"request": request, "error": None, "email": ""},
    )


@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    """Connecte un utilisateur si les identifiants sont corrects."""
    form = await request.form()
    email = form.get("email", "").strip().lower()
    password = form.get("password", "")

    user = db.query(User).filter(User.email == email).first()
    if user is None or not verify_password(password, user.password_hash):
        return auth_template(
            request,
            "login.html",
            "Adresse email ou mot de passe incorrect.",
            email,
        )

    login_user(request, user)
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/logout")
def logout(request: Request):
    """Deconnecte l'utilisateur."""
    logout_user(request)
    return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/generate-cv", response_class=HTMLResponse)
async def generate_cv(request: Request, db: Session = Depends(get_db)):
    """Sauvegarde le CV puis retourne seulement son HTML pour HTMX."""
    user = get_current_user(request, db)
    if user is None:
        return HTMLResponse(
            '<div class="preview-placeholder">Connecte-toi pour enregistrer ton CV.</div>',
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    cv = await form_to_cv_dict(request)
    save_user_cv(db, user, cv)

    return templates.TemplateResponse(
        request,
        "cv_preview.html",
        {
            "request": request,
            "cv": cv,
        },
    )


def auth_template(request: Request, template_name: str, error: str, email: str):
    """Reaffiche un formulaire d'authentification avec un message d'erreur."""
    return templates.TemplateResponse(
        request,
        template_name,
        {"request": request, "error": error, "email": email},
        status_code=status.HTTP_400_BAD_REQUEST,
    )


async def form_to_cv_dict(request: Request) -> dict:
    """Convertit les donnees du formulaire HTML en dictionnaire Python."""
    form = await request.form()

    return {
        "nom": form.get("nom", "").strip(),
        "prenom": form.get("prenom", "").strip(),
        "email": form.get("email", "").strip(),
        "telephone": form.get("telephone", "").strip(),
        "titre": form.get("titre", "").strip(),
        "resume": clean_items(form.getlist("resume")),
        "experiences": clean_items(form.getlist("experiences")),
        "formations": clean_items(form.getlist("formations")),
        "competences": clean_items(form.getlist("competences")),
        "langues": clean_items(form.getlist("langues")),
    }


def save_user_cv(db: Session, user: User, cv_data: dict):
    """Cree ou met a jour le CV associe a l'utilisateur connecte."""
    cv_record = db.query(CV).filter(CV.user_id == user.id).first()
    if cv_record is None:
        cv_record = CV(user_id=user.id)
        db.add(cv_record)

    cv_record.nom = cv_data["nom"]
    cv_record.prenom = cv_data["prenom"]
    cv_record.email = cv_data["email"]
    cv_record.telephone = cv_data["telephone"]
    cv_record.titre = cv_data["titre"]
    cv_record.resume = json.dumps(cv_data["resume"])
    cv_record.experiences = json.dumps(cv_data["experiences"])
    cv_record.formations = json.dumps(cv_data["formations"])
    cv_record.competences = json.dumps(cv_data["competences"])
    cv_record.langues = json.dumps(cv_data["langues"])

    db.commit()


def cv_record_to_dict(cv_record: CV | None, default_email: str = "") -> dict:
    """Convertit un CV SQLAlchemy en dictionnaire utilisable dans les templates."""
    if cv_record is None:
        return {
            "nom": "",
            "prenom": "",
            "email": default_email,
            "telephone": "",
            "titre": "",
            "resume": [""],
            "experiences": [""],
            "formations": [""],
            "competences": [""],
            "langues": [""],
        }

    return {
        "nom": cv_record.nom or "",
        "prenom": cv_record.prenom or "",
        "email": cv_record.email or default_email,
        "telephone": cv_record.telephone or "",
        "titre": cv_record.titre or "",
        "resume": load_list(cv_record.resume),
        "experiences": load_list(cv_record.experiences),
        "formations": load_list(cv_record.formations),
        "competences": load_list(cv_record.competences),
        "langues": load_list(cv_record.langues),
    }


def load_list(value: str | None) -> list[str]:
    """Relit une liste stockee au format JSON dans SQLite."""
    if not value:
        return [""]

    try:
        items = json.loads(value)
    except json.JSONDecodeError:
        return [""]

    if not items:
        return [""]

    return items


def clean_items(items: list[str]) -> list[str]:
    """Supprime les champs vides avant d'afficher le CV."""
    return [item.strip() for item in items if item.strip()]