from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.database import get_db
from app.models.usuario import Usuario, RefreshToken
from app.security.hashing import hash_senha, verificar_senha
from app.security.jwt_handler import criar_access_token, criar_refresh_token

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterInput(BaseModel):
    nome: str
    email: EmailStr
    senha: str


class LoginInput(BaseModel):
    email: EmailStr
    senha: str


class RefreshInput(BaseModel):
    refresh_token: str


@router.post("/register", status_code=201)
def register(data: RegisterInput, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.email == data.email).first():
        raise HTTPException(400, "Email já cadastrado")

    usuario = Usuario(
        nome=data.nome,
        email=data.email,
        senha_hash=hash_senha(data.senha)
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return {"mensagem": "Usuário criado", "id": usuario.id}


@router.post("/login")
def login(data: LoginInput, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == data.email).first()
    if not usuario or not verificar_senha(data.senha, usuario.senha_hash):
        raise HTTPException(401, "Credenciais inválidas")

    access_token  = criar_access_token(usuario.id)
    refresh_token = criar_refresh_token()

    rt = RefreshToken(token=refresh_token, usuario_id=usuario.id)
    db.add(rt)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh")
def refresh(data: RefreshInput, db: Session = Depends(get_db)):
    rt = db.query(RefreshToken).filter(
        RefreshToken.token == data.refresh_token,
        RefreshToken.expirado == False
    ).first()
    if not rt:
        raise HTTPException(401, "Refresh token inválido ou expirado")

    # Invalida o token atual (rotativo)
    rt.expirado = True

    # Cria novo par
    novo_refresh = criar_refresh_token()
    novo_rt = RefreshToken(token=novo_refresh, usuario_id=rt.usuario_id)
    db.add(novo_rt)
    db.commit()

    return {
        "access_token": criar_access_token(rt.usuario_id),
        "refresh_token": novo_refresh
    }


@router.post("/logout")
def logout(data: RefreshInput, db: Session = Depends(get_db)):
    rt = db.query(RefreshToken).filter(RefreshToken.token == data.refresh_token).first()
    if rt:
        rt.expirado = True
        db.commit()
    return {"mensagem": "Logout realizado"}
