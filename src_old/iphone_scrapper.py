# Este código solo ejecuta reiteradas veces 01_wallascrap.py con los distintos parametros 
# para IPHONE 14 15 y 16

from utils.run_wallascrap import run_wallascrap
from utils.process_and_run_jupiter import process_and_run_jupiter


# 'new', 'as_good_as_new', 'good'
def run_01_scrapper_iphone():
    item_name = 'iphone 14'
    municipio = 'Madrid'
    estado = 'new'
    distancia = '60'
    precio_minimo = '200'
    run_wallascrap(item_name, municipio, estado, distancia, precio_minimo)
    estado = 'as_good_as_new'
    run_wallascrap(item_name, municipio, estado, distancia, precio_minimo)
    estado = 'good'
    run_wallascrap(item_name, municipio, estado, distancia, precio_minimo)

    item_name = 'iphone 15'
    municipio = 'Madrid'
    estado = 'new'
    distancia = '60'
    precio_minimo = '220'
    run_wallascrap(item_name, municipio, estado, distancia, precio_minimo)
    estado = 'as_good_as_new'
    run_wallascrap(item_name, municipio, estado, distancia, precio_minimo)
    estado = 'good'
    run_wallascrap(item_name, municipio, estado, distancia, precio_minimo)

    item_name = 'iphone 16'
    municipio = 'Madrid'
    estado = 'new'
    distancia = '60'
    precio_minimo = '250'
    run_wallascrap(item_name, municipio, estado, distancia, precio_minimo)
    estado = 'as_good_as_new'
    run_wallascrap(item_name, municipio, estado, distancia, precio_minimo)
    estado = 'good'
    run_wallascrap(item_name, municipio, estado, distancia, precio_minimo)

######################################
#####        02_join_tables      #####
######################################

run_01_scrapper_iphone()
process_and_run_jupiter("02_join_tables_iphone.ipynb")
process_and_run_jupiter("03_feature_engineering_iphone.ipynb")
process_and_run_jupiter("04_download_description.ipynb")
process_and_run_jupiter("05_get_data_from_comments.ipynb")

from utils.upload_files_and_folders_to_s3 import upload_files_and_folders_to_s3
upload_files_and_folders_to_s3()
