import os

def existe_cadena(name, cadenas_buscadas, cadenas_excluyentes):
    nombre_list = name.split()
    nombre_list = set(nombre_list)
    if nombre_list.intersection(cadenas_buscadas):
        if not nombre_list.intersection(cadenas_excluyentes):
            return True
        else:
            return False
    else:
        return False

"""
Primero mira que la primera palabra sea la buscada. Para un iphone casi todos empiezan por iphone o movil.
    Si así es mira que sea el modelo, en este caso busca que ponga "iphone 16" y "phone 1 6" que por algun motivo 
    algunos usuarios ponen espacios

Si no aplica la función anterior, mucho más restrictiva. 
xx en mi caso es 16
"""
def is_iphone_xx(name, xx, cadenas_buscadas, cadenas_excluyentes):
    name_splited = name.split(" ")
    if (name_splited[0] in ("movil", "móvil", "iphone", "smartphone")): # si empieza por "movil" o similar es mucho menos restrictivo.
        if ((xx in name_splited) and ('4' not in name_splited) and ('5' not in name_splited) 
            and ('6' not in name_splited)): # para evitar que casos como 'iphone 4 16 gb azul'
            return True
        else:
            return False
    else:
        return existe_cadena(name, cadenas_buscadas, cadenas_excluyentes) # llama a ua funcion mas restrictiva


def ya_existe_articulo(id, df):
    existe = df['id'].isin([id]).any()
    return existe

def item_reservado(elem):
    try:
        elemento_reservado = elem.find_element(By.CSS_SELECTOR, ".clase_indicativa_de_reservado")
        return True
    except:
        return False



ciudades_espana = {
    "Madrid": [-3.7003454, 40.4166909],
    "A Coruña": [-8.4115401, 43.3623436],
    "Álava (Vitoria-Gasteiz)": [-2.6724431, 42.8467184],
    "Albacete": [-1.8585424, 38.994349],
    "Alicante": [-0.4906855, 38.3459963],
    "Almería": [-2.4637136, 36.834047],
    "Asturias (Oviedo)": [-5.8447595, 43.3602902],
    "Ávila": [-4.7005176, 40.6564391],
    "Badajoz": [-6.9706535, 38.8785452],
    "Barcelona": [2.1734035, 41.3850639],
    "Burgos": [-3.696906, 42.3439925],
    "Cáceres": [-6.3724247, 39.4752765],
    "Cádiz": [-6.2885955, 36.5270612],
    "Cantabria (Santander)": [-3.8044431, 43.4623057],
    "Castellón de la Plana": [-0.037261, 39.9863563],
    "Ciudad Real": [-3.9271012, 38.986307],
    "Córdoba": [-4.7791517, 37.8881758],
    "Cuenca": [-2.1330719, 40.0703925],
    "Girona": [2.8249323, 41.9794005],
    "Granada": [-3.588141, 37.1773363],
    "Guadalajara": [-3.161852, 40.6290199],
    "Guipúzcoa (San Sebastián)": [-1.9783706, 43.3183347],
    "Huelva": [-6.944722, 37.261421],
    "Huesca": [-0.4085092, 42.1401],
    "Jaén": [-3.7889245, 37.7795941],
    "Las Palmas de Gran Canaria": [-15.4134306, 28.1235459],
    "León": [-5.5669243, 42.5987263],
    "Lleida": [0.6267957, 41.6175899],
    "Lugo": [-7.5567581, 43.0098773],
    "Málaga": [-4.4213988, 36.7213028],
    "Murcia": [-1.1306544, 37.9922399],
    "Navarra (Pamplona)": [-1.6440833, 42.812526],
    "Ourense": [-7.8638804, 42.337229],
    "Palencia": [-4.5318699, 42.009079],
    "Pontevedra": [-8.6443548, 42.431041],
    "Salamanca": [-5.6635397, 40.9701039],
    "Segovia": [-4.1183825, 40.9480835],
    "Sevilla": [-5.9844589, 37.3890924],
    "Soria": [-2.4688326, 41.7640127],
    "Tarragona": [1.2486664, 41.118883],
    "Teruel": [-1.106878, 40.3446275],
    "Toledo": [-4.0273231, 39.8628316],
    "Valencia": [-0.3759513, 39.4699075],
    "Valladolid": [-4.728562, 41.652251],
    "Zamora": [-5.7446601, 41.5034086],
    "Zaragoza": [-0.8870568, 41.6496933],
    "Ceuta": [-5.3076631, 35.8893873],
    "Melilla": [-2.9380973, 35.2922778],
    "Palma de Mallorca": [2.6501603, 39.5696005],
    "Ibiza (Eivissa)": [1.4326344, 38.9087485],
    "Mahón (Menorca)": [4.2585759, 39.889093],
    "Formentera (Sant Francesc)": [1.444653, 38.6962491],
    "Santa Cruz de Tenerife (Tenerife)": [-16.2518467, 28.4636296],
    "San Sebastián de La Gomera (La Gomera)": [-17.1033464, 28.0915289],
    "Puerto del Rosario (Fuerteventura)": [-13.8622846, 28.5017114],
    "Arrecife (Lanzarote)": [-13.5379374, 28.9613805],
    "Valverde (El Hierro)": [-17.918344, 27.8094396],
    "San Cristóbal de La Laguna (Tenerife)": [-16.3159063, 28.4852765]
}

class Color:
    ROJO = '\033[91m'
    VERDE = '\033[92m'
    VERDE_OSCURO = '\033[38;5;22m'
    AMARILLO = '\033[93m'
    AZUL_CLARO = '\033[94m'
    MAGENTA = '\033[95m'
    CIAN = '\033[96m'
    RESET = '\033[0m'
