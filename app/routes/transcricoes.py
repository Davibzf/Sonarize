from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.transcricao import Transcricao
from app.models.usuario import Usuario
from app.security.dependencias import usuario_atual
from app.services.audio_worker import processar_audio
import os
import uuid

router = APIRouter(prefix="/transcricoes", tags=["transcrições"])

FORMATOS_PERMITIDOS = {".mp3", ".mp4", ".wav", ".m4a", ".ogg"}
TAMANHO_MAX_MB = 50


@router.post("", status_code=202)
async def criar_transcricao(
    background_tasks: BackgroundTasks,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(usuario_atual)
):
    # Valida extensão
    ext = os.path.splitext(arquivo.filename)[1].lower()
    if ext not in FORMATOS_PERMITIDOS:
        raise HTTPException(400, f"Formato não suportado. Use: {FORMATOS_PERMITIDOS}")

    # Lê e valida tamanho
    conteudo = await arquivo.read()
    if len(conteudo) > TAMANHO_MAX_MB * 1024 * 1024:
        raise HTTPException(400, f"Arquivo muito grande. Máximo: {TAMANHO_MAX_MB}MB")

    # Salva arquivo temporariamente
    nome_unico = f"{uuid.uuid4()}{ext}"
    caminho    = f"uploads/{nome_unico}"
    with open(caminho, "wb") as f:
        f.write(conteudo)

    # Cria registro no banco
    transcricao = Transcricao(
        usuario_id=usuario.id,
        nome_arquivo=arquivo.filename,
        status="pendente"
    )
    db.add(transcricao)
    db.commit()
    db.refresh(transcricao)

    # CORRIGIDO: worker abre sua própria sessão — não passa db
    background_tasks.add_task(processar_audio, transcricao.id, caminho)

    return {"job_id": transcricao.id, "status": "pendente"}


@router.get("/{id}/status")
def status_transcricao(
    id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(usuario_atual)
):
    t = db.query(Transcricao).filter(
        Transcricao.id == id,
        Transcricao.usuario_id == usuario.id
    ).first()
    if not t:
        raise HTTPException(404, "Transcrição não encontrada")
    return {"id": t.id, "status": t.status, "erro": t.erro_msg}


@router.get("/{id}/resumo")
def ver_resumo(
    id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(usuario_atual)
):
    t = db.query(Transcricao).filter(
        Transcricao.id == id,
        Transcricao.usuario_id == usuario.id
    ).first()
    if not t:
        raise HTTPException(404, "Não encontrada")
    if t.status != "concluido":
        raise HTTPException(400, f"Status atual: {t.status}. Aguarde o processamento.")
    return {
        "id": t.id,
        "arquivo": t.nome_arquivo,
        "transcricao": t.transcricao,
        "resumo": t.resumo,
        "concluido_em": t.concluido_em
    }


@router.get("")
def listar_transcricoes(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(usuario_atual)
):
    offset = (page - 1) * limit
    total  = db.query(Transcricao).filter(Transcricao.usuario_id == usuario.id).count()
    items  = db.query(Transcricao).filter(
        Transcricao.usuario_id == usuario.id
    ).order_by(Transcricao.criado_em.desc()).offset(offset).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "pages": -(-total // limit),
        "items": [
            {
                "id": t.id,
                "arquivo": t.nome_arquivo,
                "status": t.status,
                "criado_em": t.criado_em
            }
            for t in items
        ]
    }
