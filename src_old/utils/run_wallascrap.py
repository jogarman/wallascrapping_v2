import os
import subprocess
import sys

############################### 
###### xxxxx_scraper.py ####### 
############################### 
def run_wallascrap(item_name, municipio, estado, distancia, precio_minimo):
    print("def run_wallascrap...")
    # Use the current interpreter from the activated virtualenv
    python_executable = sys.executable
    command = [
        python_executable, '01_wallascrap.py',
        '--item_name', item_name,
        '--municipio', municipio,
        '--estado', estado,
        '--distancia', str(distancia),
        '--precio_minimo', str(precio_minimo)
    ]
    print("command: ", command)
    # Use the same environment as the parent process (virtualenv activated)
    result = subprocess.run(command, capture_output=True, text=True, env=os.environ)
    print("stdout: ", result.stdout)
    if result.stderr:
        print("stderr: ", result.stderr)