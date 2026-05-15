import pymongo
from datetime import datetime

def poblar_base_datos():
    # Conexión a la base de datos local
    try:
        # Intentamos conectar al puerto por defecto de MongoDB
        cliente = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        cliente.server_info() # Verificamos que el servidor responde
        print("Conexión exitosa a MongoDB.")
    except pymongo.errors.ServerSelectionTimeoutError:
        print("Error: No se pudo conectar a MongoDB.")
        return

    # Creación de la base de datos y la colección
    db = cliente["SistemaBiblioteca"]
    coleccion_libros = db["libros"]  

    # Limpieza de la colección para evitar duplicados si se ejecuta varias veces
    coleccion_libros.delete_many({})

    # Colección de libros
    libros = [
        {
            "titulo": "Cien Años",
            "genero": "Ficción",
            "fecha_ingreso": datetime(2025, 5, 10),
            "ubicacion": {"pasillo": "A", "estante": 1},
            "historial_prestamos": [
                {"usuario": "juan_perez", "estado": "devuelto"},
                {"usuario": "maria_g", "estado": "activo"}
            ]
        },
        {
            "titulo": "El Principito",
            "genero": "Infantil",
            "fecha_ingreso": datetime(2025, 8, 22),
            "ubicacion": {"pasillo": "B", "estante": 2},
            "historial_prestamos": [
                {"usuario": "luis_rojas", "estado": "devuelto"}
            ]
        },
        {
            "titulo": "1984",
            "genero": "Ficción",
            "fecha_ingreso": datetime(2026, 1, 5),
            "ubicacion": {"pasillo": "C", "estante": 3},
            "historial_prestamos": []
        },
        {
            "titulo": "Don Quijote",
            "genero": "Clásico",
            "fecha_ingreso": datetime(2024, 11, 15),
            "ubicacion": {"pasillo": "A", "estante": 1},
            "historial_prestamos": [
                {"usuario": "carlos_v", "estado": "devuelto"},
                {"usuario": "ana_s", "estado": "devuelto"}
            ]
        },
        {
            "titulo": "Pinocho",
            "genero": "Infantil",
            "fecha_ingreso": datetime(2026, 3, 10),
            "ubicacion": {"pasillo": "D", "estante": 4},
            "historial_prestamos": [
                {"usuario": "pedro_m", "estado": "activo"}
            ]
        },
        {
            "titulo": "Fahrenheit",
            "genero": "Ficción",
            "fecha_ingreso": datetime(2025, 12, 1),
            "ubicacion": {"pasillo": "C", "estante": 2},
            "historial_prestamos": [
                {"usuario": "laura_p", "estado": "devuelto"}
            ]
        },
        {
            "titulo": "Hábitos Atómicos",
            "genero": "Autoayuda",
            "fecha_ingreso": datetime(2026, 4, 20),
            "ubicacion": {"pasillo": "E", "estante": 1},
            "historial_prestamos": []
        },
        {
            "titulo": "Sapiens",
            "genero": "Historia",
            "fecha_ingreso": datetime(2025, 2, 28),
            "ubicacion": {"pasillo": "E", "estante": 3},
            "historial_prestamos": [
                {"usuario": "diego_f", "estado": "activo"}
            ]
        },
        {
            "titulo": "Red Dead",
            "genero": "Ficción",
            "fecha_ingreso": datetime(2024, 7, 14),
            "ubicacion": {"pasillo": "C", "estante": 1},
            "historial_prestamos": [
                {"usuario": "martin_t", "estado": "devuelto"},
                {"usuario": "sofia_l", "estado": "activo"}
            ]
        },
        {
            "titulo": "La Metamorfosis",
            "genero": "Clásico",
            "fecha_ingreso": datetime(2025, 9, 5),
            "ubicacion": {"pasillo": "A", "estante": 2},
            "historial_prestamos": []
        },
        {
            "titulo": "Padre Rico",
            "genero": "Autoayuda",
            "fecha_ingreso": datetime(2026, 2, 18),
            "ubicacion": {"pasillo": "E", "estante": 2},
            "historial_prestamos": [
                {"usuario": "andres_c", "estado": "devuelto"}
            ]
        },
        {
            "titulo": "El Hobbit",
            "genero": "Ficción", 
            "fecha_ingreso": datetime(2025, 6, 30),
            "ubicacion": {"pasillo": "D", "estante": 2},
            "historial_prestamos": [
                {"usuario": "lucas_h", "estado": "devuelto"},
                {"usuario": "valeria_r", "estado": "devuelto"}
            ]
        },
        {
            "titulo": "Los Miserables",
            "genero": "Clásico",
            "fecha_ingreso": datetime(2024, 10, 10),
            "ubicacion": {"pasillo": "A", "estante": 3},
            "historial_prestamos": [
                {"usuario": "camila_b", "estado": "activo"}
            ]
        },
        {
            "titulo": "Rebelión",
            "genero": "Ficción",
            "fecha_ingreso": datetime(2026, 1, 15),
            "ubicacion": {"pasillo": "B", "estante": 1},
            "historial_prestamos": []
        },
        {
            "titulo": "Detective Conan",
            "genero": "Misterio",
            "fecha_ingreso": datetime(2025, 4, 12),
            "ubicacion": {"pasillo": "F", "estante": 1},
            "historial_prestamos": [
                {"usuario": "roberto_q", "estado": "devuelto"},
                {"usuario": "paula_m", "estado": "devuelto"},
                {"usuario": "ivan_r", "estado": "activo"}
            ]
        },
        {
            "titulo": "Mundo Feliz",
            "genero": "Ficción",
            "fecha_ingreso": datetime(2025, 11, 25),
            "ubicacion": {"pasillo": "C", "estante": 4},
            "historial_prestamos": [
                {"usuario": "esteban_d", "estado": "devuelto"}
            ]
        }
    ]

    #Inserción de los datos
    if libros:
        # Usamos insert_many para enviar toda la lista de una vez
        resultado = coleccion_libros.insert_many(libros)
        print(f"¡Éxito total! Se insertaron {len(resultado.inserted_ids)} libros con los títulos nuevos.")
    else:
        print("La lista de libros está vacía.")

if __name__ == "__main__":
    poblar_base_datos()