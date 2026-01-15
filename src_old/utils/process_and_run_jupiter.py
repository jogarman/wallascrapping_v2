import shutil
import os
from nbconvert import PythonExporter
import nbformat
import subprocess

def is_jupyter(file):
    if file[-6:] == '.ipynb':
        return True
    else:
        return False
    
def convert_ipynb_to_py(jupyter_file):
    """
    Convierte un archivo {nombre}.ipynb en un archivo {nombre}.py en la misma carpeta.

    """
    if not is_jupyter(jupyter_file):
        print(f"{jupyter_file} debe ser un archivo .ipynb")
        return
    with open(jupyter_file, 'r', encoding='utf-8') as f:
        notebook = nbformat.read(f, as_version=4)
    python_exporter = PythonExporter()
    body, _ = python_exporter.from_notebook_node(notebook)
    python_file = os.path.splitext(jupyter_file)[0] + '.py'
    with open(python_file, 'w', encoding='utf-8') as f:
        f.write(body)
    print(f"Archivo convertido: {python_file}")

def delete_file(file):
    if os.path.exists(file):
        os.remove(file)
        print(f"{file} ha sido eliminado")
    else:
        print(f"No se puede borrar {file}. No existe")
def run_py(program):
    print("Ejecutando: ", "python", program)
    subprocess.run(["python", program])

def move_to_build(file):
    """
    Copia y sobreescribe el archivo a la carpeta ../build
    """
    shutil.copy(file, os.path.join("..", "build", file))


def process_and_run_jupiter(jupiter_file):
    """
    Steps:
      1. Verify that the file is a Jupyter Notebook (.ipynb).
      2. Check if a corresponding .py file exists one directory up.
         - If it does not exist, convert the .ipynb to a .py file.
      3. Execute the generated .py file.
      4. Delete the generated .py file after execution.
    """
    if not is_jupyter(jupiter_file):
        print(f"{jupiter_file} debe ser .ipynb")
        return
    python_file = jupiter_file[:-6] + '.py'
    if not os.path.exists(os.path.join("..", python_file)): # comprueba si ya existe
        print(f"Convirtiendo {jupiter_file}...")
        convert_ipynb_to_py(jupiter_file)
        #move_to_build(python_file)
    else:
        print(f"{python_file} Ya existe.")
    try:
        run_py(python_file)
    except Exception as e:
        print(f"Error al ejecutar {python_file}: {e}")
    delete_file(python_file)