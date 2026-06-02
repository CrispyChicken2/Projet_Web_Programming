from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    cv = relationship(
        "CV",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )


class CV(Base):
    __tablename__ = "cvs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    nom = Column(String(120), default="")
    prenom = Column(String(120), default="")
    email = Column(String(255), default="")
    telephone = Column(String(60), default="")
    titre = Column(String(180), default="")

    resume = Column(Text, default="[]")
    experiences = Column(Text, default="[]")
    formations = Column(Text, default="[]")
    competences = Column(Text, default="[]")
    langues = Column(Text, default="[]")

    user = relationship("User", back_populates="cv")
