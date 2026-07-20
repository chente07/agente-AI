from django.db import models


class Analisis(models.Model):
    imagen = models.ImageField(upload_to="radiografias/")
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Análisis {self.id}"