# Scrapea las gopros 10, 11 y 12
# NO FUNCIONA BIEN
# Este código solo ejecuta reiteradas veces 01_wallascrap.py con los distintos parametros 
# para gopro 10, 11 y 12
# luego hace las transformaciones necesarias

from utils.run_wallascrap import run_wallascrap
from utils.process_and_run_jupiter import process_and_run_jupiter


#############################################
##### 01_wallascrap gopros 10, 11 y 12 ######
#############################################

# 'new', 'as_good_as_new', 'good'
def run_01_scrapper_gopro():
    item_name = 'gopro 10'
    municipio = 'Madrid'
    estado = 'new'
    distancia = '60'
    precio_minimo = '60'
    run_wallascrap(item_name, municipio, estado, distancia, precio_minimo)
    estado = 'as_good_as_new'
    run_wallascrap(item_name, municipio, estado, distancia, precio_minimo)
    estado = 'good'
    run_wallascrap(item_name, municipio, estado, distancia, precio_minimo)

    item_name = 'gopro 11'
    municipio = 'Madrid'
    estado = 'new'
    distancia = '60'
    precio_minimo = '70'
    run_wallascrap(item_name, municipio, estado, distancia, precio_minimo)
    estado = 'as_good_as_new'
    run_wallascrap(item_name, municipio, estado, distancia, precio_minimo)
    estado = 'good'
    run_wallascrap(item_name, municipio, estado, distancia, precio_minimo)

    item_name = 'gopro 12'
    municipio = 'Madrid'
    estado = 'new'
    distancia = '60'
    precio_minimo = '80'
    run_wallascrap(item_name, municipio, estado, distancia, precio_minimo)
    estado = 'as_good_as_new'
    run_wallascrap(item_name, municipio, estado, distancia, precio_minimo)
    estado = 'good'
    run_wallascrap(item_name, municipio, estado, distancia, precio_minimo)

    item_name = 'gopro 13'
    municipio = 'Madrid'
    estado = 'new'
    distancia = '60'
    precio_minimo = '90'
    run_wallascrap(item_name, municipio, estado, distancia, precio_minimo)
    estado = 'as_good_as_new'
    run_wallascrap(item_name, municipio, estado, distancia, precio_minimo)
    estado = 'good'
    run_wallascrap(item_name, municipio, estado, distancia, precio_minimo)

######################################
#####        02_join_tables      #####
######################################

run_01_scrapper_gopro()
process_and_run_jupiter("02_join_tables_gopro.ipynb")
process_and_run_jupiter("03_feature_engineering_gopro.ipynb")
from utils.upload_files_and_folders_to_s3 import upload_files_and_folders_to_s3
upload_files_and_folders_to_s3()

