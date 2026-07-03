from django import forms
from PIL import Image

from .models import Analisis


class AnalisisForm(forms.ModelForm):
    class Meta:
        model = Analisis
        fields = ["imagen"]

        widgets = {
            "imagen": forms.ClearableFileInput(
                attrs={
                    "accept": ".jpg,.jpeg,.png",
                    "id": "image-input",
                }
            )
        }

    def clean_imagen(self):
        imagen = self.cleaned_data.get("imagen")

        if not imagen:
            raise forms.ValidationError(
                "Debe seleccionar una imagen."
            )

        formatos_permitidos = {
            "image/jpeg",
            "image/png",
        }

        if imagen.content_type not in formatos_permitidos:
            raise forms.ValidationError(
                "Formato no permitido. Solo se aceptan archivos JPG, JPEG o PNG."
            )

        tamaño_maximo = 5 * 1024 * 1024

        if imagen.size > tamaño_maximo:
            raise forms.ValidationError(
                "La imagen no debe superar los 5 MB."
            )

        try:
            archivo = Image.open(imagen)
            archivo.verify()
        except Exception:
            raise forms.ValidationError(
                "El archivo seleccionado no es una imagen válida o está dañado."
            )

        imagen.seek(0)

        return imagen