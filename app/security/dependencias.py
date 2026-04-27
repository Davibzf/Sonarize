from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.security.jwt_handler import decodificar_token
from app.models.usuario import Usuario

bearer = HTTPBearer()


def usuario_atual(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db)
) -> Usuario:
    token = credentials.credentials
    try:
        payload = decodificar_token(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    usuario = db.query(Usuario).filter(
        Usuario.id == int(payload["sub"])
    ).first()

    if not usuario or not usuario.ativo:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    return usuario
