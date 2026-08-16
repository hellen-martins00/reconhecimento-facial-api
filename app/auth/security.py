from datetime import datetime, timedelta, timezone

from jose import jwt

from app.config import SECRET_KEY


ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


def criar_token_acesso(
    agente_id: str
):

    expiracao = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": agente_id,
        "exp": expiracao
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token