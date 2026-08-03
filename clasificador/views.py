from django.shortcuts import render

from .forms import AnalisisForm
from .services.predictor import predecir_radiografia


def inicio(request):
    return render(request, "clasificador/inicio.html")


def analizar(request):
    analisis = None
    resultado = None
    confianza = None
    confianza_torax = None
    es_torax = None
    mensaje_modelo = None
    error_analisis = None
    mensaje_interpretativo = None

    if request.method == "POST":
        formulario = AnalisisForm(request.POST, request.FILES)

        if formulario.is_valid():
            analisis = formulario.save()

            try:
                prediccion = predecir_radiografia(
                    analisis.imagen.path
                )

                resultado = prediccion["resultado"]
                confianza = prediccion["confianza"]
                es_torax = prediccion["es_torax"]
                mensaje_modelo = prediccion["mensaje"]
                confianza_torax = prediccion.get("confianza_torax")

                if not es_torax:
                    mensaje_interpretativo = (
                        "La imagen no corresponde a una radiografía de tórax. "
                        "Seleccione una imagen válida para ejecutar el análisis pulmonar."
                    )

                elif resultado == "NORMAL":
                    mensaje_interpretativo = (
                        "No se detectaron patrones compatibles con neumonía "
                        "en la imagen analizada."
                    )

                elif resultado == "NEUMONIA":
                    mensaje_interpretativo = (
                        "Se detectaron patrones compatibles con neumonía. "
                        "Se recomienda consultar a un profesional de la salud."
                    )

                elif resultado == "OTRA_ENFERMEDAD":
                    mensaje_interpretativo = (
                        "La imagen no corresponde a un pulmón sano ni presenta un patrón "
                        "típico de neumonía. Podría tratarse de otra afección pulmonar. "
                        "Se recomienda consultar a un profesional de la salud."
                    )

                else:
                    mensaje_interpretativo = (
                        "El modelo generó una clasificación no reconocida. "
                        "Revise la configuración de clases del modelo."
                    )

            except Exception as error:
                error_analisis = (
                    "No fue posible analizar la imagen. "
                    "Verifique que los modelos estén instalados correctamente."
                )

                print(f"Error de predicción: {error}")

    else:
        formulario = AnalisisForm()

    resultado_texto = resultado.replace("_", " ") if resultado else None

    contexto = {
        "formulario": formulario,
        "analisis": analisis,
        "resultado": resultado,
        "resultado_texto": resultado_texto,
        "confianza": confianza,
        "confianza_torax": confianza_torax,
        "es_torax": es_torax,
        "mensaje_modelo": mensaje_modelo,
        "error_analisis": error_analisis,
        "mensaje_interpretativo": mensaje_interpretativo,
    }

    return render(
        request,
        "clasificador/analizar.html",
        contexto
    )