from django.shortcuts import render

from .forms import AnalisisForm


def inicio(request):
    return render(request, "clasificador/inicio.html")


def analizar(request):
    analisis = None

    if request.method == "POST":
        formulario = AnalisisForm(request.POST, request.FILES)

        if formulario.is_valid():
            analisis = formulario.save()
    else:
        formulario = AnalisisForm()

    contexto = {
        "formulario": formulario,
        "analisis": analisis,
    }

    return render(request, "clasificador/analizar.html", contexto)