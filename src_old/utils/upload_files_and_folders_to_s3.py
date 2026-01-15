import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

# # Crear cliente de S3
# s3 = boto3.client('s3')

# # Especificar el bucket y la carpeta local
# bucket_name = 'data-wallascrap'
# local_folder = '../data'

def upload_files_and_folders_to_s3(local_folder='../data', bucket_name='data-wallascrap'):
    s3 = boto3.client('s3')
    # Recorre todos los directorios y archivos en la carpeta local
    for root, dirs, files in os.walk(local_folder):
        for file in files:
            # Construir la ruta completa del archivo local
            local_path = os.path.join(root, file)
            
            # Construir la ruta en el bucket de S3
            relative_path = os.path.relpath(local_path, local_folder)
            s3_path = relative_path.replace("\\", "/")  # Asegura que se usen separadores de ruta de S3

            try:
                # Comprobar si el archivo ya existe en el bucket
                s3.head_object(Bucket=bucket_name, Key=s3_path)
                print(f'El archivo {s3_path} ya existe en el bucket.')
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    # El archivo no existe, proceder con la carga
                    try:
                        s3.upload_file(local_path, bucket_name, s3_path)
                        print(f'Subido {local_path} a s3://{bucket_name}/{s3_path}')
                    except FileNotFoundError:
                        print(f'El archivo {local_path} no fue encontrado.')
                    except NoCredentialsError:
                        print('Credenciales no disponibles para acceder a S3.')
                    except Exception as e:
                        print(f'Error al subir {local_path}. Error: {e}')
                else:
                    # Si ocurre un error distinto, imprimirlo
                    print(f'Error al verificar el archivo {s3_path}. Error: {e}')

# Llamar a la función para subir archivos y carpetas
upload_files_and_folders_to_s3()