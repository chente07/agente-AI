from django import forms
from .models import Analisis


class AnalisisForm(forms.ModelForm):
    class Meta:
        model = Analisis
        fields = ["imagen"]

        widgets = {
            "imagen": forms.ClearableFileInput(
                attrs={
                    "accept": ".jpg,.jpeg,.png"
                }
            )
        }