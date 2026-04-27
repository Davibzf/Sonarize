from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id         = Column(Integer, primary_key=True)
    nome       = Column(String(100), nullable=False)
    email      = Column(String(150), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    ativo      = Column(Boolean, default=True)
    criado_em  = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    transcricoes   = relationship("Transcricao", back_populates="usuario")
    refresh_tokens = relationship("RefreshToken", back_populates="usuario")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id         = Column(Integer, primary_key=True)
    token      = Column(String(500), unique=True, nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)  # CORRIGIDO
    expirado   = Column(Boolean, default=False)
    criado_em  = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    usuario = relationship("Usuario", back_populates="refresh_tokens")
