from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database import create_tables, get_connection
from models import Tipo, Hurto, UsuarioRegistrado, Token
from auth import hashear_password, verficar_password, crear_token, obtener_usuario_actual
import psycopg

# py -m uvicorn main:app --reload

app = FastAPI()

create_tables()

@app.get("/")
def inicio():
    return {"mensaje": "API funcionando correctamente"}  

@app.post("/tipos")
def create_type(type: Tipo, usuario_actual: dict = Depends(obtener_usuario_actual)):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("INSERT INTO " \
                "tipoHurto (nombre) VALUES(%s)" 
                "RETURNING id", 
                (type.nombre,))
    
    new_id = cur.fetchone()["id"]

    conn.commit()
    cur.close()
    conn.close()

    return {"mensaje": "Tipo de Hurto creado", "id": new_id};

@app.get("/tipos")
def listar_type():

    conn = get_connection()

    type = conn.execute(
        "SELECT * FROM tipoHurto"
    ).fetchall()

    conn.close()

    return [dict(x) for x in type]

@app.get("/tipos/{id}")
def search_type(id: int):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT nombre FROM tipoHurto WHERE id = %s", (id,))

    type = cur.fetchone()

    cur.close()
    conn.close()

    if type:
        return type
    raise HTTPException(status_code=404, detail="Tipo de hurto no encontrado")

@app.delete("/tipos/{id}")
def delete_type(id: int, usuario_actual: dict = Depends(obtener_usuario_actual)):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
    "DELETE FROM tipoHurto WHERE id=%s",
    (id,)
    )

    affect_rows = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()

    if affect_rows == 0:
        raise HTTPException(status_code=404, detail="Tipo de Hurto no encontrado")
    return {"mensaje": "Tipo de Hurto eliminado exitosamente"}   

@app.post("/hurtos")
def create_hurto(hurto: Hurto, usuario_actual: dict = Depends(obtener_usuario_actual)):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM tipoHurto WHERE id = %s",
                (hurto.tipoHurto_id,))
    
    if not cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="El tipo de hurto no existe")
    
    cur.execute("INSERT INTO " \
                "hurtos (denunciante, direccion, fechaHurto, tipoHurto_id) VALUES(%s, %s, %s, %s)" 
                "RETURNING id", 
                (hurto.denunciante, hurto.direccion, hurto.fechaHurto, hurto.tipoHurto_id))
    new_id = cur.fetchone()["id"]

    conn.commit()
    cur.close()
    conn.close()
    return {"mensaje": "Hurto creado", "id": new_id};

@app.get("/hurtos")
def listar_hurtos():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM hurtos ORDER BY id"
    )

    hurtos = cur.fetchall()
    conn.close()
    cur.close()

    return hurtos

@app.get("/hurtos/{id}")
def search_hurto(id: int):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, denunciante, direccion, fechaHurto, fechaRegistro, tipoHurto_id FROM hurtos WHERE id = %s", (id,))

    hurto = cur.fetchone()

    cur.close()
    conn.close()

    if hurto:
        return hurto
    raise HTTPException(status_code=404, detail="hurto no encontrado")

@app.put("/hurtos/{id}")
def update_hurto(id: int, hurto: Hurto, usuario_actual: dict = Depends(obtener_usuario_actual)):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("UPDATE hurtos SET denunciante = %s, direccion = %s, fechaHurto = %s, tipoHurto_id = %s WHERE id = %s", 
                (hurto.denunciante, hurto.direccion, hurto.fechaHurto, hurto.tipoHurto_id, id))

    affect_rows = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()

    if affect_rows == 0:
        raise HTTPException(status_code = 404, detail = "hurto no encontrado")
    return {"mensaje": "hurto actualizado exitosamente"}

@app.delete("/hurtos/{id}")
def delete_hurto(id: int, usuario_actual: dict = Depends(obtener_usuario_actual)):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
    "DELETE FROM hurtos WHERE id=%s",
    (id,)
    )

    affect_rows = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()

    if affect_rows == 0:
        raise HTTPException(status_code=404, detail="hurto no encontrado")
    return {"mensaje": "hurto eliminado exitosamente"}

@app.post("/registro")
def registrar_usuario(usuario: UsuarioRegistrado):

    conn = get_connection()
    cur = conn.cursor()

    password_hash = hashear_password(usuario.password)

    try:
        cur.execute(
            "INSERT INTO usuarios (username, password_hash)" \
            "VALUES (%s, %s) RETURNING id",
            (usuario.username, password_hash)
        )

        nuevo_id = cur.fetchone()["id"]
        conn.commit()

    except psycopg.errors.UniqueViolation:
        conn.rollback()
        cur.close()
        conn.close()

        raise HTTPException(status_code=400, detail="Ese nombre de usuario ya existe.")

    cur.close()
    conn.close()

    return {"mensaje": "Usuario registrado", "id": nuevo_id}

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, username, password_hash FROM usuarios WHERE  username = %s",
        (form_data.username,)
    )

    usuario = cur.fetchone()
    cur.close()
    conn.close()

    if not usuario or verficar_password(
        form_data.password, usuario["password_hash"
                                    ]):
        token = crear_token({"sub": usuario["username"], "id": usuario["id"]})

    return {"access_token": token, "token_type": "bearer"}