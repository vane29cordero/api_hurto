import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg.connect(DATABASE_URL, row_factory = dict_row)

def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tipoHurto (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL
            )
        """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS hurtos (
            id SERIAL PRIMARY KEY,
            denunciante VARCHAR(100) NOT NULL,
            direccion VARCHAR(100) NOT NULL,
            fechaHurto DATE,
            fechaRegistro DATE DEFAULT CURRENT_DATE,
            tipoHurto_id INTEGER NOT NULL,
            CONSTRAINT fk_tipo_hurto
                FOREIGN KEY (tipoHurto_id)
                REFERENCES tipoHurto(id)
                ON DELETE RESTRICT
            )
        """)
    
    conn.commit()
    cur.close()
    conn.close()

