from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Transcricao(Base):
    __tablename__ = "transcricoes"

    id           = Column(Integer, primary_key=True)
    usuario_id   = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    nome_arquivo = Column(String(255), nullable=False)
    status       = Column(String(50), default="pendente")
    # status possíveis: pendente | processando | concluido | erro
    transcricao  = Column(Text, nullable=True)
    resumo       = Column(Text, nullable=True)
    duracao_s    = Column(Float, nullable=True)
    erro_msg     = Column(String(500), nullable=True)
    criado_em    = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    concluido_em = Column(DateTime, nullable=True)

    usuario = relationship("Usuario", back_populates="transcricoes")
