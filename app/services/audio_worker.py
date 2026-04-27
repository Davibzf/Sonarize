import whisper
import google.generativeai as genai
from datetime import datetime, timezone
from app.config import settings
from app.database import SessionLocal
import os

genai.configure(api_key=settings.GEMINI_API_KEY)

# Carrega o modelo Whisper uma vez na inicialização
model_whisper = whisper.load_model("base")


def processar_audio(transcricao_id: int, caminho_arquivo: str):
    """
    Worker que abre sua própria sessão de banco.
    NÃO recebe db como parâmetro — evita sessão fechada após a request.
    """
    db = SessionLocal()
    try:
        # Importa aqui para evitar circular import
        from app.models.transcricao import Transcricao

        transcricao = db.query(Transcricao).filter(Transcricao.id == transcricao_id).first()
        if not transcricao:
            return

        transcricao.status = "processando"
        db.commit()

        # 1. Transcrição com Whisper
        resultado = model_whisper.transcribe(caminho_arquivo)
        texto = resultado["text"]

        # 2. Resumo com Gemini
        model_gemini = genai.GenerativeModel("gemini-pro")
        resposta = model_gemini.generate_content(
            f"Faça um resumo claro e objetivo do seguinte texto transcrito de áudio:\n\n{texto}"
        )

        transcricao.transcricao  = texto
        transcricao.resumo       = resposta.text
        transcricao.status       = "concluido"
        transcricao.concluido_em = datetime.now(timezone.utc)

    except Exception as e:
        if transcricao:
            transcricao.status   = "erro"
            transcricao.erro_msg = str(e)[:500]

    finally:
        db.commit()
        db.close()
        # Remove arquivo após processar
        if os.path.exists(caminho_arquivo):
            os.remove(caminho_arquivo)
