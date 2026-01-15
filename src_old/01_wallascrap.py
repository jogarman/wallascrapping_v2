# %%
import time
import pandas as pd
import numpy as np
from datetime import datetime
from utils.get_if_same_csv_exists import *
import os

from utils.utils import *

#import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager # type: ignore
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#from selenium.webdriver.common.keys import Keys
#from bs4 import BeautifulSoup
#from selenium.webdriver.common.action_chains import ActionChains

# %% [markdown]
# Define: ```Elemento a buscar``` ```Estado``` ```distancia``` ```n_scrolls_cada_vez```
#  ```Lista a incluir``` 
#  ```Lista a excluir```

import sys
# sys.argv es una lista que contiene los argumentos
# El primer elemento es el nombre del archivo .py
# Los siguientes son los parámetros pasados
import argparse

# Crear un parser de argumentos
parser = argparse.ArgumentParser(description="Procesa algunos parámetros de entrada.")

parser.add_argument('--item_name', type=str, help="El primer parámetro", required=True)
parser.add_argument('--municipio', type=str, help="El segundo parámetro", required=True)
parser.add_argument('--estado', type=str, help="El tercer parámetro", required=True)
parser.add_argument('--distancia', type=str, help="El cuarto parámetro", required=True)
parser.add_argument('--precio_minimo', type=str, help="El quinto parámetro", required=True)

# Parsear los argumentos
args = parser.parse_args()

print(f"Escrapeo en curso: ")
print(f"{args.item_name}")
print(f"{args.municipio}")
print(f"{args.estado}")
print(f"{args.distancia}")
print(f"{args.precio_minimo}")

# Crea el txt con los outputs de errores
output_folder = 'scrapping_outputs'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
now = datetime.now()
formatted_date = now.strftime("%Y%m%d_%H%M")
item_name_formatted = args.item_name.replace(" ", "_")  
estado_formatted = args.estado.replace(" ", "_")
file_name = f"{formatted_date}_{item_name_formatted}_{estado_formatted}.txt"
file_path = os.path.join(output_folder, file_name)
sys.stdout = open(file_path, 'w', encoding='utf-8')

# %%
#ejecutar con el entorno .env
elemento_a_buscar = args.item_name
n_iphone = elemento_a_buscar.split()[1] # para otros elementos modificlar el bucle que verifica si el item es correcto

#funcion para seleccionar los articulos que quiero:
# si una la tiene o no la tiene se incluye o excluye.
# por ejemplo si buscadas = 15 y 16
#                excluyentes = funda cristal
#                'funda iphone 15' se excluye
#                'iphone'      no se incluye porque no tiene el 15 ni el 16
cadenas_buscadas = (
                    n_iphone,
                    n_iphone + ',',
                    n_iphone + '.'
                    )  # la coma es para que python lo vea como una tupla
cadenas_excluyentes = (
                    "pantalla",
                    "pantallas",
                    "funda",
                    "fundas",
                    "carcasa",
                    "carcasas",
                    "protector",
                    "cristal",
                    "3", "4", "5", "6",
                    "4s", "5s", "6s"
                    "16gb",
                    "caja",
                    "macbook"
)

n_excluidos_seguidos_max = 30
n_scrolls_cada_vez = 25 

estado = args.estado
distancia = args.distancia # distancia en km
municipio = args.municipio
precio_min = int(args.precio_minimo)
carpeta ="../data/1_datos_raw"
if type(cadenas_buscadas) is not tuple:
    print("cadenas_buscadas no es tupla")
if type(estado) is not str:
    print("estado no es str") 
    
# %%
# Abre la ventana en modo headless
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--enable-unsafe-webgl')
options.add_argument('--disable-usb')

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

ele_1 = elemento_a_buscar.split()[0]
ele_2 = elemento_a_buscar.split()[1]
#driver.get('https://es.wallapop.com');
# para Madrid no cambiar las coordenadas
url = 'https://es.wallapop.com/app/search?filters_source=quick_filters&keywords=' + ele_1 + '%20' + ele_2 + '&longitude=-3.69196&latitude=40.41956&distance='+ str(distancia) + '000&condition=' + str(estado)
driver.get(url)
print(url)
time.sleep(1)
driver.maximize_window()  
driver.switch_to.window(driver.current_window_handle)
driver.implicitly_wait(1)

# %%
WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler"))
    ).click()


# %%
# Scroll para llegar al boton para cargar mas
n = 0
while n < 5:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    n = n + 1

# %%
# Clicamos para ver más
print("click: boton_ver_mas")
boton_ver_mas = WebDriverWait(driver, 6).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "#btn-load-more")))
boton_ver_mas.click()
time.sleep(2)

# %%
# Creación de la tabla con las columnas que buscamos
columnas = [
    'id', 'time_scrap', 'nombre', 'precio', 'estado', 'reservado',
    'municipio', 'distancia', 'url_articulo'
     ]

df = pd.DataFrame(columns=columnas)

# %%
time.sleep(2)
x_coord = 1600
y_coord = 780 
# pyautogui.click(x=x_coord, y=y_coord) #######

# %% [markdown]
# # Scrolling

# %%
# Clicamos para ver más y hacemos scroll down n veces
n = 0
try:
    while n < n_scrolls_cada_vez:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        n += 1
        print(f"scroll {n}")
except Exception as e:
    print(f"Ocurrió un error: {e}")

# %%
def item_reservado(elem):
    # Asumiendo que la clase 'reservado' en algún elemento interno indica que el artículo está reservado
    try:
        elemento_reservado = elem.find_element(By.CSS_SELECTOR, ".clase_indicativa_de_reservado")
        return True
    except:
        return False

# %%
def es_precio_ok(precio: str, precio_min: int):
    precio = precio.replace(".", "TEMP").replace(",", ".").replace("TEMP", ",")
    precio = float(precio)
    if precio >= precio_min: 
        return 1
    else:
        return 0

# %%
sys.stdout.reconfigure(encoding='utf-8')
# Extraigo los datos y los añado en la tabla. 
print("Extrayendo y añadiendo los datos...")
elementos = driver.find_elements(By.CSS_SELECTOR, "a.ItemCardList__item")
total_elementos =  len(elementos)
n_excluidos_seguidos = 0
print(df.columns)
for index, elem in enumerate(elementos):
    if n_excluidos_seguidos >= n_excluidos_seguidos_max:
        break
    pos = (str(index) + "/" + str(total_elementos))
    url_articulo = elem.get_attribute('href')
    id = url_articulo.split('-')[-1]
    if not ya_existe_articulo(id, df):
        nombre = elem.get_attribute('title')
        nombre = nombre.lower()
        if is_iphone_xx(nombre, n_iphone, cadenas_buscadas, cadenas_excluyentes):
            precio = elem.find_element(By.CSS_SELECTOR, ".ItemCard__price").text.strip()
            precio = precio.split(' ')[0]
            if es_precio_ok(precio, precio_min):
                reservado = item_reservado(elem)
                time_scrap = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Guarda en la tabla
                print(pos, "++ guardado   ++ " + nombre)
                df.loc[index] = [
                    id, time_scrap, nombre, precio, estado, reservado,
                    municipio, distancia, url_articulo]
                n_excluidos_seguidos = 0
            else:
                print(pos, "--precio bajo -- ", precio, nombre)
        else:
            n_excluidos_seguidos = n_excluidos_seguidos + 1
            print(pos, "## excluido   ## ", nombre)
    else:
        print(pos, "** ya existe:  ** ", nombre, id)
        n_excluidos_seguidos = 0

df = df.reset_index(drop=True)
print(df)

# %%
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
df

# %%
hoy_formateada = formatted_date.split('_')[0]
#hoy_formateada = datetime.now().strftime("%Y%m%d")
vez_que_busca_en_el_dia = get_if_same_csv_exists(hoy_formateada, elemento_a_buscar, estado)
print(hoy_formateada)
print(vez_que_busca_en_el_dia)
print(elemento_a_buscar)
print(estado)
nombre_archivo_csv = hoy_formateada + '_' + vez_que_busca_en_el_dia + '_' \
    + elemento_a_buscar + '_' + estado
if not os.path.exists(carpeta):
    os.makedirs(carpeta)
df = df.reset_index(drop=True) # sin indice
df.to_csv(os.path.join(carpeta, nombre_archivo_csv + '.csv'))
# %%
try:
    df = pd.read_csv(carpeta + '/' + nombre_archivo_csv + '.csv')
    print("csv guardado")
    driver.quit()
except:
    print("Error leyendo archivo! puede que no se haya guardado bien")

