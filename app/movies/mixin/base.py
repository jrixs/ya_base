
import uuid
from django.db import models


class TimeStampedMixin(models.Model):
    """ Абстрактная модель
    Дабавляет поля с дотой и временем создания и изменения в модели
    наследующие этот класс.
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    """ Абстрактная модель
    Дабавляет поля id в модели наследующие этот класс.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
