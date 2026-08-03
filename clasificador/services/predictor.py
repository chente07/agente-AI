import json
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn as nn
from django.conf import settings
from PIL import Image
from torchvision import models, transforms
from ultralytics import YOLO


MODEL_TORAX_PATH = (
    Path(settings.BASE_DIR)
    / "clasificador"
    / "ml_models"
    / "modelo_torax.pt"
)

MODEL_NEUMONIA_PATH = (
    Path(settings.BASE_DIR)
    / "clasificador"
    / "ml_models"
    / "modelo_neumonia.pt"
)

CLASES_NEUMONIA_PATH = (
    Path(settings.BASE_DIR)
    / "clasificador"
    / "ml_models"
    / "clases_neumonia.json"
)

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

_modelo_torax = None
_modelo_neumonia = None
_clases_neumonia = None
_transform_neumonia = None


def obtener_modelo_torax():
    global _modelo_torax

    if _modelo_torax is None:
        if not MODEL_TORAX_PATH.exists():
            raise FileNotFoundError(
                f"No se encontró el modelo de tórax en: {MODEL_TORAX_PATH}"
            )

        _modelo_torax = YOLO(str(MODEL_TORAX_PATH))

    return _modelo_torax


def _obtener_metadatos_neumonia():
    global _clases_neumonia

    if _clases_neumonia is None:
        if not CLASES_NEUMONIA_PATH.exists():
            raise FileNotFoundError(
                f"No se encontró el archivo de clases en: {CLASES_NEUMONIA_PATH}"
            )

        with open(CLASES_NEUMONIA_PATH, "r", encoding="utf-8") as archivo:
            _clases_neumonia = json.load(archivo)

    return _clases_neumonia


def _crear_arquitectura(model_name, num_clases):
    if model_name == "inception_v3":
        # transform_input=True es obligatorio: así se construye el modelo cuando se entrena
        # con weights=Inception_V3_Weights.IMAGENET1K_V1 (torchvision lo activa automáticamente).
        # No es parte del state_dict, así que hay que fijarlo igual aquí a mano o la inferencia
        # ve una entrada renormalizada distinta a la que el modelo aprendió.
        modelo = models.inception_v3(
            weights=None, aux_logits=True, init_weights=False, transform_input=True
        )
        modelo.fc = nn.Linear(modelo.fc.in_features, num_clases)
        modelo.AuxLogits.fc = nn.Linear(modelo.AuxLogits.fc.in_features, num_clases)

    elif model_name == "vgg16":
        modelo = models.vgg16(weights=None)
        modelo.classifier[6] = nn.Linear(modelo.classifier[6].in_features, num_clases)

    elif model_name == "mobilenet_v3_large":
        modelo = models.mobilenet_v3_large(weights=None)
        modelo.classifier[3] = nn.Linear(modelo.classifier[3].in_features, num_clases)

    elif model_name == "resnet50":
        modelo = models.resnet50(weights=None)
        modelo.fc = nn.Linear(modelo.fc.in_features, num_clases)

    else:
        raise ValueError(f"Arquitectura de modelo no soportada: {model_name}")

    return modelo


def obtener_modelo_neumonia():
    global _modelo_neumonia

    if _modelo_neumonia is None:
        if not MODEL_NEUMONIA_PATH.exists():
            raise FileNotFoundError(
                f"No se encontró el modelo de neumonía en: {MODEL_NEUMONIA_PATH}"
            )

        metadatos = _obtener_metadatos_neumonia()
        clases = metadatos["clases"]

        modelo = _crear_arquitectura(metadatos["model_name"], num_clases=len(clases))
        estado = torch.load(str(MODEL_NEUMONIA_PATH), map_location=DEVICE)
        modelo.load_state_dict(estado)
        modelo.to(DEVICE)
        modelo.eval()

        _modelo_neumonia = modelo

    return _modelo_neumonia


def _recortar_bordes_negros(imagen, umbral_intensidad=15, fraccion_minima=0.15):
    """Recorta barras/márgenes negros (con texto de metadatos, reglas, etc.)
    conservando solo la región donde la mayoría de los píxeles tienen contenido real.
    """
    gris = np.array(imagen.convert("L"), dtype=np.float32)

    fraccion_por_columna = (gris > umbral_intensidad).mean(axis=0)
    fraccion_por_fila = (gris > umbral_intensidad).mean(axis=1)

    columnas_validas = np.where(fraccion_por_columna > fraccion_minima)[0]
    filas_validas = np.where(fraccion_por_fila > fraccion_minima)[0]

    if columnas_validas.size == 0 or filas_validas.size == 0:
        return imagen

    izquierda, derecha = int(columnas_validas[0]), int(columnas_validas[-1])
    arriba, abajo = int(filas_validas[0]), int(filas_validas[-1])

    return imagen.crop((izquierda, arriba, derecha + 1, abajo + 1))


def _normalizar_contraste(imagen):
    """Ecualización de histograma adaptativa (CLAHE), para que el modelo no dependa
    del contraste/brillo específico de la fuente de cada radiografía.
    """
    gris = np.array(imagen.convert("L"))
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    ecualizada = clahe.apply(gris)
    return Image.fromarray(ecualizada).convert("RGB")


def _obtener_transform_neumonia():
    global _transform_neumonia

    if _transform_neumonia is None:
        metadatos = _obtener_metadatos_neumonia()
        tamano_imagen = 299 if metadatos["model_name"] == "inception_v3" else 224
        tamano_resize = round(tamano_imagen / 0.875)

        _transform_neumonia = transforms.Compose(
            [
                transforms.Lambda(_recortar_bordes_negros),
                transforms.Lambda(_normalizar_contraste),
                transforms.Resize((tamano_resize, tamano_resize)),
                transforms.CenterCrop((tamano_imagen, tamano_imagen)),
                transforms.ToTensor(),
                transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
            ]
        )

    return _transform_neumonia


def predecir_radiografia(ruta_imagen):
    modelo_torax = obtener_modelo_torax()

    resultado_torax = modelo_torax.predict(
        source=str(ruta_imagen),
        verbose=False,
    )[0]

    if resultado_torax.probs is None:
        raise RuntimeError(
            "El modelo de tórax no devolvió probabilidades de clasificación."
        )

    indice_torax = int(resultado_torax.probs.top1)
    clase_torax = resultado_torax.names[indice_torax]
    confianza_torax = float(resultado_torax.probs.top1conf) * 100

    if clase_torax.upper() != "TORAX":
        return {
            "es_torax": False,
            "resultado": "NO_TORAX",
            "confianza": round(confianza_torax, 2),
            "mensaje": "La imagen no corresponde a una radiografía de tórax.",
        }

    modelo_neumonia = obtener_modelo_neumonia()
    transform_neumonia = _obtener_transform_neumonia()
    metadatos_neumonia = _obtener_metadatos_neumonia()
    clases_neumonia = metadatos_neumonia["clases"]
    umbral_confianza = metadatos_neumonia.get("umbral_confianza", 0.75)

    imagen = Image.open(ruta_imagen).convert("RGB")
    tensor_imagen = transform_neumonia(imagen).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        salida = modelo_neumonia(tensor_imagen)
        probabilidades = torch.softmax(salida, dim=1)[0]

    indice_neumonia = int(torch.argmax(probabilidades).item())
    probabilidad_maxima = float(probabilidades[indice_neumonia].item())
    confianza_neumonia = probabilidad_maxima * 100

    if probabilidad_maxima < umbral_confianza:
        clase_neumonia = "OTRA_ENFERMEDAD"
    else:
        clase_neumonia = clases_neumonia[indice_neumonia]

    return {
        "es_torax": True,
        "resultado": clase_neumonia.upper(),
        "confianza": round(confianza_neumonia, 2),
        "confianza_torax": round(confianza_torax, 2),
        "mensaje": "La imagen fue clasificada correctamente.",
    }