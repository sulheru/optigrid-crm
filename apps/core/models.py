from django.db import models


class RuntimeSetting(models.Model):
    """
    Ajuste persistido de plataforma.

    - key: nombre lógico del ajuste
    - value: valor serializado como texto
    - updated_at: trazabilidad mínima
    """
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField(blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["key"]

    def __str__(self) -> str:
        return f"{self.key}={self.value}"
