from django.db import models
from model_utils.models import TimeStampedModel
from model_utils.models import UUIDModel

# Create your models here.

class TimestampedUUIDModel(UUIDModel, TimeStampedModel):
    class Meta:
        abstract = True

