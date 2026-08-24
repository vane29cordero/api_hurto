import os
import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 1

def hashear_password(password: str) -> str:

    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)

    return hashed.decode('utf-8')

def verficar_password(password_plano: str, password_hash: str) -> bool:

    pwd_bytes = password_plano.encode('utf-8')
    hash_bytes = password_hash.encode('utf-8')

    return bcrypt.checkpw(pwd_bytes, hash_bytes)

def crear_token(datos: dict) -> str:

    datos_a_codificar = datos.copy()

    expiracion = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)

    datos_a_codificar.update({"exp": expiracion})

    token = jwt.encode(datos_a_codificar, SECRET_KEY,
                       algorithm=ALGORITHM)

    return token

def verificar_token(token: str) -> dict:

    try:
        paylod = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])

        return paylod

    except JWTError:
        raise ValueError("Token inválido o expirado")

def obtener_usuario_actual(token: str = Depends(oauth2_scheme)) -> dict:

    try: 
        payload = verificar_token(token)

    except ValueError:
        raise HTTPException(
            status_code=404,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload