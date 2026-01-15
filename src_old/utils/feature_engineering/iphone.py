import re
import pandas as pd

#########################
## Para nombre ##########
#########################
def asignar_gen(nombre):
    if '14' in nombre:
        return '14'
    elif '15' in nombre:
        return '15'
    elif '16' in nombre:
        return '16'
    return "n/a"

# Función para asignar el valor de la columna "modelo"
def asignar_modelo(nombre):
    if 'pro max' in nombre.lower():
        return 'pro max'
    elif 'pro' in nombre.lower():
        return 'pro'
    elif 'plus' in nombre.lower():
        return 'plus'
    else:
        return 'basic'

def asignar_memoria(nombre):
    if '128' in nombre.lower():
        return '128'
    elif '256' in nombre.lower():
        return '256'
    elif '512' in nombre.lower():
        return '512'
    elif '1tb' in nombre.lower():
        return '1tb'
    else:
        return 'n/a'

# Función para asignar el valor de la columna "bateria"
def asignar_bateria(nombre):
    # Buscar números entre 80 y 100 en el nombre
    bateria = re.findall(r'\b([8-9][0-9]|100)\b', nombre)
    if bateria:
        return int(bateria[0])  # Retorna el primer número que encuentra
    return "n/a"

# Imprimir todos los colores
colores_iphones = ["Púrpura", "Verde", "Blanco", "Azul", "Negro", "Rojo", "Grafito", "Plata", "Oro", "Morado", "titanio", "Ultramarino", 'rojo', 'azul', 'negro', 'blanco', 'verde', 'amarillo', 'rosado', 'rosa', 'gris', 'morado', 'naranja']

def tiene_color(nombre):
    return any(color in nombre.lower() for color in colores_iphones)
def tiene_emojis(nombre):
    return bool(re.search(r'[^\w\s,]', nombre))  # Busca caracteres no alfanuméricos que son emojis
def tiene_vendo(nombre):
    return 'vendo' in nombre.lower()
def tiene_revisado(nombre):
    return 'revisado' in nombre.lower()


#########################
## Para comentario ######
#########################
def encontrar_bateria(texto: str):
    # Verificar si el texto es NaN o similar
    if pd.isna(texto):
        return None
    # Buscar números seguidos por %
    numeros_con_porcentaje = re.findall(r'\b(8[0-9]|9[0-9]|100)\b%', texto)
    # Si encuentra números con %, devolver el primero
    if numeros_con_porcentaje:
        return numeros_con_porcentaje[0] 
    # Si no hay % buscar solo los números
    numeros = re.findall(r'\b(8[0-9]|9[0-9]|100)\b', texto)
    # Si encuentra números, devolver el primero
    if numeros:
        return numeros[0]
    # Si no encuentra ningún número, devolver None
    return None
# buscar 128|256|512 seguido de \s*(Mb|MB|mb)
# si no, buscar \b1[Tt]\b
# si no, buscar \b(128|256|512)\b
def encontrar_memoria(texto: str) -> str:
    if pd.isna(texto):
        return None
    texto = str(texto)
    
    # Buscar 128|256|512 seguido de \s*(Mb|MB|mb)
    memorias_con_unidades = re.search(r'\b(128|256|512)\b\s*(Mb|MB|mb)', texto)
    if memorias_con_unidades:
        memoria, unidad = memorias_con_unidades.groups()
        return memoria + unidad
    
    # Buscar \b1[Tt]\b
    memoria_1t = re.search(r'\b1[Tt]', texto)
    if memoria_1t:
        return '_1T'
    
    # Buscar \b(128|256|512)\b
    memorias_sin_unidades = re.search(r'\b(128|256|512)\b', texto)
    if memorias_sin_unidades:
        return memorias_sin_unidades.group(0)
    
    return None
    
def es_tienda(texto: str) -> bool:
    if pd.isna(texto):
        return None
    words_to_find = ('reacondicionado', 'tienda')
    for word in words_to_find:
        if word in texto:
            return True 
    return False 

def tiene_garantia(texto: str):
    if pd.isna(texto):
        return None
    words_to_find = ('garantia', 'care', 'factura')
    for word in words_to_find:
        if word in texto:
            return True 
    return False 