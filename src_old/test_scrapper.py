# FOR TEST ONLY
from utils.run_wallascrap import run_wallascrap
from utils.process_and_run_jupiter import process_and_run_jupiter
from utils.get_if_same_csv_exists import *
import pandas as pd

# 'new', 'as_good_as_new', 'good'
def run_01_test():
    item_name = 'iphone 16'
    municipio = 'Madrid'
    estado = 'new'
    distancia = '60'
    precio_minimo = '100'
    run_wallascrap(item_name, municipio, estado, distancia, precio_minimo)
    estado = 'as_good_as_new'
    run_wallascrap(item_name, municipio, estado, distancia, precio_minimo)




######################################
#####        02_join_tables      #####
######################################

import os
from datetime import datetime

import glob

# init
fecha = datetime.now().strftime("%Y%m%d")
#fecha = "20250117"
product = 'iphone'
carpeta_origen = "../data/3_feature_engineering"
carpeta_destino = "../data/4_download_description"

# Funciona!
def get_missing_records_from_csv(old_download_description, last_feature_engineering):
    """ Devuelve una serie con los id de los registros 
    que están en el segundo archivo pero no en el primero.
    Es decir, con los ids a scrappear
    """
    print(f"Comparando los archivos:\n- {old_download_description}\n- {last_feature_engineering}")
    df1 = pd.read_csv(old_download_description)
    df2 = pd.read_csv(last_feature_engineering)
    df_merged = df2.merge(df1, on='id', how='left', indicator=True)
    missing_records = df_merged[df_merged['_merge'] == 'left_only']
    return missing_records['id']
def get_old_download_description(path_product_data_n):
    """
    Busca el archivo de download_description del scrap anterior de ese dia 
    y si no del anterior
    si 
    path_product_data_n = '../data/3_feature_engineering/iphone_20250225_1.csv'
    return ../data/4_download_description/iphone_20250225_0.csv 
    siempre que iphone_20250225_0 existe. También buscaria el dia de antes
    """
    base_name = os.path.basename(path_product_data_n)
    date_str = base_name.split('_')[1]
    n = base_name.split('_')[-1].split('.')[0]
    if n != '0':
        old_n = str(int(n) - 1)
        old_download_description = f"{carpeta_destino}/iphone_{date_str}_{old_n}.csv"
    else:
        date_obj = datetime.datetime.strptime(date_str, '%Y%m%d')
        previous_day = date_obj - datetime.timedelta(days=1)
        previous_day_str = previous_day.strftime('%Y%m%d')
        pattern = f"{carpeta_destino}/iphone_{previous_day_str}_*.csv"
        files = glob.glob(pattern)
        if files:
            max_n = max([int(os.path.basename(f).split('_')[-1].split('.')[0]) for f in files])
            old_download_description = f"{carpeta_destino}/iphone_{previous_day_str}_{max_n}.csv"
        else:
            old_download_description = None
    if not old_download_description:
        print(f"No se encontraron archivos para el día anterior {previous_day_str}")
    return old_download_description

# Ejemplo de uso
last_feature_engineering = '../data/3_feature_engineering/iphone_20250225_1.csv'
def get_serie_with_id_to_scrap(last_feature_engineering):
    old_download_description = get_old_download_description(last_feature_engineering)
    print("old_download_description", old_download_description)
    return(get_missing_records_from_csv(old_download_description, last_feature_engineering))

run_01_test()
process_and_run_jupiter('02_join_tables_iphone.ipynb')
process_and_run_jupiter('03_feature_engineering_iphone.ipynb')
process_and_run_jupiter('04_download_description.ipynb')
process_and_run_jupiter('05_get_data_from_comments.ipynb')


######################################
#####        Copy to s3          #####
######################################
#from utils.upload_files_and_folders_to_s3 import upload_files_and_folders_to_s3
#upload_files_and_folders_to_s3()