import pymongo
from datetime import datetime

# Conexión a la Base de Datos
def conectar_bd():
    try:
        cliente = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        cliente.server_info() # Verificamos que el servidor responde
        db = cliente["SistemaBiblioteca"]
        return db["libros"]
    except pymongo.errors.ServerSelectionTimeoutError:
        print("Error: No se pudo conectar a MongoDB.")
        return None

# Función para listar los libros (Read)
def listar_libros(coleccion):
    print("\n--- CATÁLOGO DE LIBROS ---")
    # Utilizamos find para traer todo
    # El {"_id": 0} oculta el ID automatico de Mongo para que se vea más limpio
    libros = coleccion.find({}, {"_id": 0})
    
    contador = 0
    for libro in libros:
        contador += 1
        # Mostramos los datos básicos y la ubicación, pero no el historial de préstamos para no saturar la vista
        print(f"{contador}. {libro.get('titulo')} - {libro.get('genero')}")
        print(f"   Ubicación: Pasillo {libro['ubicacion']['pasillo']}, Estante {libro['ubicacion']['estante']}")
        print("-" * 30)
    
    if contador == 0:
        print("No hay libros registrados en la base de datos.")

        # Función para crear un nuevo libro (Create)
def crear_libro(coleccion):
    print("\n--- AGREGAR NUEVO LIBRO ---")
    
    # Pedimos los datos básicos por consola
    titulo = input("Ingresa el título del libro: ")
    genero = input("Ingresa el género: ")
    pasillo = input("Ingresa el pasillo (ej. A, B, C, D, E, F): ")
    
    # Protección contra errores para el número de estante
    while True:
        try:
            # input() guarda texto así que usamos int() para forzarlo a ser un número
            estante = int(input("Ingresa el número de estante: "))
            break # Si se escribió un número, rompemos este ciclo y avanzamos
        except ValueError:
            print("Error: El estante debe ser un número entero.")

    # Armamos el documento que irá a MongoDB
    nuevo_libro = {
        "titulo": titulo,
        "genero": genero,
        "fecha_ingreso": datetime.now(), # Genera automáticamente la fecha y hora actual
        "ubicacion": {
            "pasillo": pasillo,
            "estante": estante
        },
        "historial_prestamos": [] # Inicia como una lista vacía, ya que es nuevo
    }

    # 4. Lo guardamos en la base de datos
    resultado = coleccion.insert_one(nuevo_libro)
    
    # 5. Confirmación visual
    if resultado.inserted_id:
        print(f"\n¡Éxito! El libro '{titulo}' fue agregado correctamente a la base de datos.")


       # Función para buscar por operadores (Read básico)
def buscar_por_operadores(coleccion):
    print("\n--- BÚSQUEDA POR GÉNERO ---") #Operadores de comparación: $in, $ne, $gt, $lt, etc.
    print("1. Buscar libros de géneros específicos") #$in
    print("2. Buscar libros excluyendo un género")#$ne
    
    sub_opcion = input("Elige una opción (1 o 2): ")
    
    if sub_opcion == '1':
        print("\nGeneros disponibles: Ficción, Clásico, Infantil, Autoayuda, Historia, Misterio")
        entrada = input("Ingresa los géneros separados por coma: ")
        
        # Limpiamos los espacios en blanco
        lista_generos = [g.strip() for g in entrada.split(",")]
        consulta = {"genero": {"$in": lista_generos}}
        
    elif sub_opcion == '2':
        excluir = input("\nIngresa el género que deseas EXCLUIR (Ficción, Clásico, Infantil, Autoayuda, Historia, Misterio): ")
        consulta = {"genero": {"$ne": excluir.strip()}}
        
    else:
        print("Opción inválida. Volviendo al menú principal...")
        return

    # APLICAMOS LA COLACIÓN PARA IGNORAR TILDES Y MAYÚSCULAS
    # locale "es" = Reglas del idioma español
    # strength 1 = Ignora mayúsculas, minúsculas y tildes
    reglas_espanol = {"locale": "es", "strength": 1}
    
    resultados = list(coleccion.find(consulta, {"_id": 0}).collation(reglas_espanol))
    
    if len(resultados) > 0:
        print(f"\n¡Se encontraron {len(resultados)} libros!")
        for libro in resultados:
            print(f"- {libro.get('titulo')} (Género: {libro.get('genero')})")
    else:
        print("\nNo se encontraron libros con ese criterio.")

# Función para buscar usando expresión regular (Read avanzado)
def buscar_por_regex(coleccion):
    print("\n--- BÚSQUEDA AVANZADA POR TÍTULO ---")
    palabra_clave = input("Ingresa una palabra o fragmento del título a buscar: ")
    
    # Armamos la consulta con $regex
    # $options: "i" le dice a MongoDB que ignore las mayúsculas y minúsculas
    consulta = {"titulo": {"$regex": palabra_clave, "$options": "i"}}
    
    # Ejecutamos la búsqueda aplicando proyección
    resultados = list(coleccion.find(consulta, {"_id": 0}))
    
    if len(resultados) > 0:
        print(f"\n¡Se encontraron {len(resultados)} libros que contienen '{palabra_clave}'!")
        for libro in resultados:
            print(f"- {libro.get('titulo')} (Pasillo: {libro['ubicacion']['pasillo']})")
    else:
        print(f"\nNo se encontraron libros que contengan la palabra '{palabra_clave}'.")

# Función para buscar por rango de fechas (Read avanzado)
def buscar_por_fechas(coleccion):
    print("\n--- BÚSQUEDA POR RANGO DE FECHAS ---")
    print("El formato debe ser AAAA-MM-DD (ejemplo: 2025-05-15)")
    
    # Protección contra errores para el formato de fecha
    while True:
        try:
            fecha_inicio_str = input("Ingresa la fecha de INICIO (AAAA-MM-DD): ")
            fecha_fin_str = input("Ingresa la fecha de FIN (AAAA-MM-DD): ")
            
            # strptime transforma el texto en un objeto 'datetime'
            # %Y = Año (4 dígitos), %m = Mes (2 dígitos), %d = Día (2 dígitos)
            fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d")
            fecha_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d")
            break # Si el formato es correcto, rompemos el ciclo y avanzamos
        except ValueError:
            print("Error: Formato incorrecto. Usa guiones y el orden AAAA-MM-DD.")

    # Armamos la consulta usando $gte (mayor o igual) y $lte (menor o igual)
    consulta = {
        "fecha_ingreso": {
            "$gte": fecha_inicio,
            "$lte": fecha_fin
        }
    }
    
    # Ejecutamos la búsqueda aplicando la proyección requerida
    resultados = list(coleccion.find(consulta, {"_id": 0}))
    
    if len(resultados) > 0:
        print(f"\nSe encontraron {len(resultados)} libros ingresados en ese rango")
        for libro in resultados:
            # strftime convierte el objeto 'datetime' de vuelta a texto con el formato que elijamos
            fecha_formateada = libro.get('fecha_ingreso').strftime("%d/%m/%Y")
            print(f"- {libro.get('titulo')} (Ingresado el: {fecha_formateada})")
    else:
        print("\nNo se encontraron libros en ese rango de fechas.")

# Función para buscar en subdocumentos y arrays (Read avanzado)
def buscar_anidado(coleccion):
    print("\n--- BÚSQUEDA EN ESTRUCTURAS ANIDADAS ---")
    print("1. Buscar por Pasillo (Dentro de un subdocumento)")
    print("2. Buscar Historial de Usuario (Dentro de un array)")
    
    sub_opcion = input("Elige una opción (1 o 2): ")
    
    if sub_opcion == '1':
        pasillo = input("\nIngresa la letra del pasillo a buscar (ej. A, B, C, D, E, F): ").upper()
        # Para acceder a un campo dentro de un subdocumento usamos la notación de puntos: "ubicacion.pasillo"
        consulta = {"ubicacion.pasillo": pasillo}
        mensaje = f"ubicados en el pasillo '{pasillo}'"
        
    elif sub_opcion == '2':
        usuario = input("\nIngresa el nombre de usuario: ").lower()
        # Para buscar dentro de un array de subdocumentos, usamos la notación de puntos y el nombre del campo del array: "historial_prestamos.usuario"
        consulta = {"historial_prestamos.usuario": usuario}
        mensaje = f"que han sido prestados al usuario '{usuario}'"
        
    else:
        print("Opción inválida. Volviendo al menú principal")
        return

    # Ejecutamos la búsqueda aplicando la proyección requerida
    resultados = list(coleccion.find(consulta, {"_id": 0}))
    
    if len(resultados) > 0:
        print(f"\n¡Se encontraron {len(resultados)} libros {mensaje}!")
        for libro in resultados:
            print(f"- {libro.get('titulo')} (Género: {libro.get('genero')})")
    else:
        print(f"\nNo se encontraron libros {mensaje}.")

# Función para actualizar un campo de la raíz (Update)
def actualizar_simple(coleccion):
    print("\n--- ACTUALIZAR GÉNERO DE UN LIBRO ---")
    
    # Pedimos el título exacto
    titulo_buscar = input("Ingresa el título exacto del libro a modificar: ")
    
    # Buscamos el documento antes de modificarlo usando find_one
    libro_antes = coleccion.find_one({"titulo": titulo_buscar}, {"_id": 0})
    
    # Si libro_antes es None (no existe), detenemos la función
    if not libro_antes:
        print(f"Error: No se encontró ningún libro con el título '{titulo_buscar}'.")
        return

    # Imprimimos el estado original
    print("\n--- Documento antes de la modificación ---")
    print(libro_antes)
    
    # Pedimos el nuevo dato
    nuevo_genero = input(f"\nIngresa el nuevo género para '{titulo_buscar}': ")
    
    # Realizamos la actualización usando el operador $set
    filtro = {"titulo": titulo_buscar}
    nuevos_valores = {"$set": {"genero": nuevo_genero}}
    
    coleccion.update_one(filtro, nuevos_valores)
    
    # Buscamos el documento después de la modificación
    libro_despues = coleccion.find_one({"titulo": titulo_buscar}, {"_id": 0})
    
    print("\n--- Documento después de la modificación ---")
    print(libro_despues)
    print("\nActualización exitosa")

# Función para actualizar dentro de un array (Update avanzado)
def actualizar_avanzado(coleccion):
    print("\n--- REGISTRAR NUEVO PRÉSTAMO ---")#Array de subdocumentos: historial_prestamos
    
    # Pedimos el título exacto
    titulo_buscar = input("Ingresa el título exacto del libro a prestar: ")
    
    # Buscamos el documento ANTES de modificarlo
    libro_antes = coleccion.find_one({"titulo": titulo_buscar}, {"_id": 0})
    
    if not libro_antes:
        print(f"Error: No se encontró ningún libro con el título '{titulo_buscar}'.")
        return

    # Imprimimos el estado original
    print("\n--- Documento ANTES de la modificación ---")
    print(libro_antes)
    
    # Pedimos los datos del nuevo préstamo
    nuevo_usuario = input("\nIngresa el nombre del usuario que pide el libro: ").lower()
    
    # Armamos el diccionario del subdocumento que irá dentro de la lista
    nuevo_prestamo = {
        "usuario": nuevo_usuario,
        "estado": "activo"
    }
    
    # Realizamos la actualización usando el operador $push
    filtro = {"titulo": titulo_buscar}
    nuevos_valores = {"$push": {"historial_prestamos": nuevo_prestamo}}
    
    coleccion.update_one(filtro, nuevos_valores)
    
    # Buscamos el documento después de la modificación
    libro_despues = coleccion.find_one({"titulo": titulo_buscar}, {"_id": 0})
    
    print("\n--- Documento después de la modificación ---")
    print(libro_despues)
    print(f"\nPréstamo de '{titulo_buscar}' a '{nuevo_usuario}' registrado exitosamente")

# Función para eliminar un libro (Delete)
def eliminar_libro(coleccion):
    print("\n--- ELIMINAR UN LIBRO ---")
    
    # Condición específica: Buscar por título
    titulo_borrar = input("Ingresa el título exacto del libro que deseas eliminar: ")
    
    # Buscamos el documento ANTES de borrarlo
    libro = coleccion.find_one({"titulo": titulo_borrar}, {"_id": 0})
    
    if not libro:
        print(f"Error: No se encontró ningún libro con el título '{titulo_borrar}'.")
        return

    # Mostramos el documento
    print("\nSe encontró el siguiente registro:")
    print(libro)
    
    # Solicitamos confirmación explícita
    confirmacion = input(f"\n¿Estás absolutamente seguro de eliminar '{titulo_borrar}'? (s/n): ").lower()
    
    if confirmacion == 's':
        # Ejecutamos la eliminación
        resultado = coleccion.delete_one({"titulo": titulo_borrar})
        
        # Confirmamos el resultado
        if resultado.deleted_count > 0:
            print(f"\nÉxito. El libro '{titulo_borrar}' ha sido borrado de la base de datos.")
        else:
            print("\nError al intentar eliminar el documento.")
    else:
        print("\nOperación cancelada. El libro no fue borrado.")

# Menú Principal
def menu_principal():
    coleccion = conectar_bd()
    if coleccion is None:
        return # Si no hay conexión, salimos del programa

    while True: # Este ciclo mantiene el menú repitiéndose hasta que elijas salir
        print("\n" + "="*40)
        print("   SISTEMA DE GESTIÓN DE BIBLIOTECA   ")
        print("="*40)
        print("1. Crear un nuevo libro")
        print("2. Listar todos los libros")
        print("3. Buscar por género") #Operadores usados: $ne y $in
        print("4. Busqueda avanzada por título") #$regex con $options para ignorar mayúsculas y tildes
        print("5. Buscar por rango de fechas")
        print("6. Buscar por pasillo o historial de usuarios") #Buscar en subdocumentos y arrays
        print("7. Actualizar género") #Update simple con $set
        print("8. Registrar nuevo préstamo") #Update avanzado con $push para agregar a un array
        print("9. Eliminar un libro")
        print("0. Salir del programa")
        print("="*40)
        
        opcion = input("Ingresa una opción (0-9): ")

        if opcion == '1':
            crear_libro(coleccion)

        elif opcion == '2':
            listar_libros(coleccion)

        elif opcion == '3':
            buscar_por_operadores(coleccion)

        elif opcion == '4':
            buscar_por_regex(coleccion)

        elif opcion == '5':
            buscar_por_fechas(coleccion)
    
        elif opcion == '6':
            buscar_anidado(coleccion)

        elif opcion == '7':
            actualizar_simple(coleccion)

        elif opcion == '8':
            actualizar_avanzado(coleccion)

        elif opcion == '9':
            eliminar_libro(coleccion)

        elif opcion == '0':
            print("\nSaliendo del Sistema de Biblioteca.")
            break

        else:
            print("\nOpción no válida, intenta de nuevo.")

# Punto de inicio del programa
if __name__ == "__main__":
    menu_principal()