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

            except Exception as error:
                error_analisis = (
                    "No fue posible analizar la imagen. "
                    "Verifique que los modelos estén instalados correctamente."
                )

                print(f"Error de predicción: {error}")

    else:
        formulario = AnalisisForm()

    contexto = {
        "formulario": formulario,
        "analisis": analisis,
        "resultado": resultado,
        "confianza": confianza,
        "confianza_torax": confianza_torax,
        "es_torax": es_torax,
        "mensaje_modelo": mensaje_modelo,
        "error_analisis": error_analisis,
    }

    return render(
        request,
        "clasificador/analizar.html",
        contexto
    )