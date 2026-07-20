FROM python:3.13-slim

# libgl1 y libglib2.0-0: dependencias de sistema que opencv-python (cv2) necesita para importar
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# torch/torchvision en build de CPU, mismas versiones exactas que requirements.txt,
# instalados aparte del índice oficial de PyPI para no arrastrar las ruedas con CUDA
RUN pip install --no-cache-dir \
    torch==2.13.0 \
    torchvision==0.28.0 \
    --index-url https://download.pytorch.org/whl/cpu

COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000", "--insecure"]
