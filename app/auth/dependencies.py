from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from jose import JWTError, jwt

from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.agentes.repository import AgenteRepository
from app.auth.security import SECRET_KEY, ALGORITHM


security = HTTPBearer()


def get_agente_atual(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    token = credentials.credentials

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        agente_id = payload.get("sub")

        if not agente_id:

            raise HTTPException(
                status_code=401,
                detail="Token inválido."
            )

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Token inválido ou expirado."
        )

    repository = AgenteRepository(db)

    agente = repository.buscar_por_id(
        UUID(agente_id)
    )

    if not agente:

        raise HTTPException(
            status_code=401,
            detail="Agente não encontrado."
        )

    return agente


def get_admin_atual(
    agente_atual = Depends(get_agente_atual)
):

    if agente_atual.perfil != "ADMIN":

        raise HTTPException(
            status_code=403,
            detail="Acesso permitido somente para administradores."
        )

    return agente_atual