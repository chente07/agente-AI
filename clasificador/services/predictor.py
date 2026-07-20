from pathlib import Path

from django.conf import settings
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

_modelo_torax = None
_modelo_neumonia = None


def obtener_modelo_torax():
    global _modelo_torax

    if _modelo_torax is None:
        if not MODEL_TORAX_PATH.exists():
            raise FileNotFoundError(
                f"No se encontró el modelo de tórax en: {MODEL_TORAX_PATH}"
            )

        _modelo_torax = YOLO(str(MODEL_TORAX_PATH))

    return _modelo_torax


def obtener_modelo_neumonia():
    global _modelo_neumonia

    if _modelo_neumonia is None:
        if not MODEL_NEUMONIA_PATH.exists():
            raise FileNotFoundError(
                f"No se encontró el modelo de neumonía en: {MODEL_NEUMONIA_PATH}"
            )

        _modelo_neumonia = YOLO(str(MODEL_NEUMONIA_PATH))

    return _modelo_neumonia


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

    resultado_neumonia = modelo_neumonia.predict(
        source=str(ruta_imagen),
        verbose=False,
    )[0]

    if resultado_neumonia.probs is None:
        raise RuntimeError(
            "El modelo de neumonía no devolvió probabilidades de clasificación."
        )

    indice_neumonia = int(resultado_neumonia.probs.top1)
    clase_neumonia = resultado_neumonia.names[indice_neumonia]
    confianza_neumonia = float(resultado_neumonia.probs.top1conf) * 100

    return {
        "es_torax": True,
        "resultado": clase_neumonia.upper(),
        "confianza": round(confianza_neumonia, 2),
        "confianza_torax": round(confianza_torax, 2),
        "mensaje": "La imagen fue clasificada correctamente.",
    }