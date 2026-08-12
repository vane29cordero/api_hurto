from datetime import date
from pydantic import BaseModel

class Tipo(BaseModel):
    nombre: str

class Hurto(BaseModel):
    denunciante: int
    direccion: str
    fechaHurto: date
    tipoHurto_id: int

