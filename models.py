from datetime import date
from pydantic import BaseModel

class Tipo(BaseModel):
    nombre: str

class Hurto(BaseModel):
    denunciante: str
    direccion: str
    fechaHurto: date
    tipoHurto_id: int

class UsuarioRegistrado(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str