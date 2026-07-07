import os
import cv2

ruta_dataset = "dataset_teste3"

corruptos = 0
total = 0

for carpeta in ["NORMAL", "NEUMONIA"]:

    ruta_carpeta = os.path.join(ruta_dataset, carpeta)

    for archivo in os.listdir(ruta_carpeta):

        total += 1

        ruta_archivo = os.path.join(ruta_carpeta, archivo)

        imagen = cv2.imread(ruta_archivo)

        if imagen is None:
            print(f"Archivo corrupto: {ruta_archivo}")
            corruptos += 1

print(f"\nTotal de imágenes revisadas: {total}")
print(f"Total de archivos corruptos: {corruptos}")