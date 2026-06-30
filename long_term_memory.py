import psycopg
from psycopg.rows import dict_row
import os
from dotenv import load_dotenv

class LongTermMemory:
    
    def __init__(self, database_url:str):
        self.DATABASE_URL = database_url

    # Obtener la conexión a la base de datos de PostgreSQL (Supabase)
    def get_conn(self):
        return psycopg.connect(self.DATABASE_URL, row_factory=dict_row)

    # Obtener las memorias de largo plazo almacenadas actualmente
    def get_long_term_memories(self, user_id:str, limit:int=20):
        
        with self.get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT created_at, memory 
                FROM public.largo_plazo
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (user_id, limit)
            )
            return cur.fetchall()
    
    # Insertar una nueva memoria de largo plazo
    def insert_long_term_memory(self, user_id:str, memory:str):
        print(f"Insertando memoria de largo plazo para el usuario {user_id}: {memory}")

        memory = (memory or "").strip()  # Asegurarse de que la memoria no sea None y eliminar espacios en blanco
        if not memory:
            print("Memoria vacía, no se insertará en la base de datos.")
            return  # No insertar memorias vacías

        with self.get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO public.largo_plazo (user_id, memory) VALUES (%s, %s)",
                (user_id, memory)
            )
            conn.commit()

    # Obtener la memoria en un formato de texto para el System Prompt
    def format_memories(self, memories):
        
        if not memories:
            return
        
        lines = [f"- {m['created_at']}: {m['memory']}\n" for m in memories]
        return "".join(lines)

if __name__ == "__main__":
    load_dotenv()
    ltm = LongTermMemory(os.environ.get("DATABASE_URL"))
    result = ltm.get_long_term_memories("1", limit=5)
    print(result)

    # ltm.insert_long_term_memory("1", "Memoria enviada desde Python")
    print(ltm.format_memories(result))