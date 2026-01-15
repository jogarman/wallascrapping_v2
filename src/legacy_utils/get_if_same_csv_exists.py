import os

def list_files_in_directory(carpeta):
    try:
        # Obtener la lista de archivos y directorios en la carpeta
        archivos = os.listdir(carpeta)
        
        # Imprimir cada archivo o directorio encontrado
        for archivo in archivos:
            print(archivo)
    except FileNotFoundError:
        print(f"La carpeta '{carpeta}' no existe.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")


def get_if_same_csv_exists(hoy_formateada, elemento_a_buscar, estado, carpeta = '../data/1_datos_raw'):
    # Inicializar el número de sufijo como 0
    nn = 0

    base_name_pattern = f"{hoy_formateada}_{{:01d}}_{elemento_a_buscar}_{estado}.csv"
    
    # Iterar para encontrar un nombre de archivo que no exista
    while True:
        # Formatear el nombre del archivo con el sufijo actual
 
        file_name = base_name_pattern.format(nn)
        print("file_name: ", file_name)
        # Construir la ruta completa del archivo
        file_path = os.path.join(carpeta, file_name)
        print("file_path: ", file_path)
        # Comprobar si el archivo ya existe
        if not os.path.exists(file_path):
            print("nombre disponible: ", file_name)
            break
        
        # Incrementar el número de sufijo para probar el siguiente
        nn += 1
    
    # Devolver el número de sufijo encontrado
    return str(nn)

