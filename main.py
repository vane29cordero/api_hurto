from fastapi import FastAPI, HTTPException
from database import create_tables, get_connection
from models import Tipo, Hurto

# py -m uvicorn main:app --reload

app = FastAPI()

create_tables()

@app.get("/")
def inicio():
    return {"mensaje": "API funcionando correctamente"}  

@app.post("/tipos")
def create_type(type: Tipo):

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
def delete_type(id: int):

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
def create_hurto(hurto: Hurto):

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
def listar_hurto():

    conn = get_connection()

    hurto = conn.execute(
    "SELECT * FROM hurtos"
    ).fetchall()

    conn.close()

    return [dict(x) for x in hurto]

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
def update_hurto(id: int, hurto: Hurto):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM hurtos WHERE id = %s",
        (hurto.tipoHurto_id,))

    if not cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Hurto no existe")

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
def delete_hurto(id: int):

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