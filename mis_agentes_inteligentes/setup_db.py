import sqlite3
from datetime import date
import os

def create_dummy_db():
    db_path = 'MisEventos.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Crear tabla
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            titulo TEXT,
            descripcion TEXT,
            prioridad TEXT
        )
    ''')
    
    # Limpiar tabla si existe
    cursor.execute('DELETE FROM eventos')
    
    # Insertar datos de prueba para hoy
    hoy = date.today().isoformat()
    eventos = [
        (hoy, 'Revisión de logs', 'Revisar logs del servidor de producción y corregir errores', 'Alta'),
        (hoy, 'Reunión de equipo', 'Daily standup con el equipo de desarrollo (15 min)', 'Media'),
        (hoy, 'Aprender Rust', 'Ver tutoriales sobre gestión de memoria en Rust', 'Baja'),
        ('2026-12-31', 'Fin de año', 'Fiesta de fin de año', 'Alta')
    ]
    
    cursor.executemany('''
        INSERT INTO eventos (fecha, titulo, descripcion, prioridad)
        VALUES (?, ?, ?, ?)
    ''', eventos)
    
    conn.commit()
    conn.close()
    print(f"Base de datos '{db_path}' inicializada con éxito.")
    print("Datos de prueba insertados para la fecha de hoy:", hoy)

if __name__ == "__main__":
    # Cambiamos al directorio del script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    create_dummy_db()
