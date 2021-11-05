from django.db import models
from model_utils.models import TimeStampedModel
from model_utils.models import UUIDModel

# Create your models here.

class TimestampedUUIDModel(UUIDModel, TimeStampedModel):
    class Meta:
        abstract = True


class AddressField(models.CharField):
    def __init__(self, *args, **kwargs):
        super(AddressField, self).__init__(*args, **kwargs)

    def get_prep_value(self, value):
        return str(value).lower()
