from django.shortcuts import render

from .forms import AnalisisForm


def inicio(request):
    return render(request, "clasificador/inicio.html")


def analizar(request):
    analisis = None
    resultado = None
    confianza = None

    if request.method == "POST":
        formulario = AnalisisForm(request.POST, request.FILES)

        if formulario.is_valid():
            analisis = formulario.save()

            # Resultado temporal para probar el funcionamiento.
            # Después será reemplazado por el modelo de IA.
            resultado = "PNEUMONIA"
            confianza = 87.50

    else:
        formulario = AnalisisForm()

    contexto = {
        "formulario": formulario,
        "analisis": analisis,
        "resultado": resultado,
        "confianza": confianza,
    }

    return render(
        request,
        "clasificador/analizar.html",
        contexto
    )