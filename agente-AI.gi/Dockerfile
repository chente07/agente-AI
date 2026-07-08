# 1. Usar una imagen oficial de Python ligera
FROM python:3.11-slim

# 2. Instalar librerías del sistema actualizadas para OpenCV y YOLO
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 3. Crear y movernos a la carpeta de trabajo dentro del contenedor
WORKDIR /app

# 4. Instalar PyTorch AND Torchvision emparejados perfectamente para CPU
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 5. Instalar Ultralytics desde el servidor estándar de Python
RUN pip install --no-cache-dir ultralytics

# 6. Copiar todos los archivos de tu carpeta local hacia adentro del contenedor
COPY . /app

# 7. Ejecutar tu script
CMD ["python", "filtro.py"]