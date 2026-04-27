from fastapi import FastAPI
from app.database import engine, Base
from app.routes import auth, transcricoes

# Importa models para o SQLAlchemy registrar as tabelas
import app.models.usuario
import app.models.transcricao

# Cria tabelas no banco
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sonarize Pro",
    description="API de transcrição e sumarização de áudio com Whisper + Gemini",
    version="1.0.0"
)

app.include_router(auth.router)
app.include_router(transcricoes.router)


@app.get("/")
def root():
    return {"status": "ok", "versao": "1.0.0", "docs": "/docs"}
