from django.db import models
from base.models import TimestampedUUIDModel


class NftReveal(TimestampedUUIDModel):
    slug = models.CharField(max_length=256, unique=True)
    contract_address = models.CharField(max_length=256)
    latest_token_id = models.IntegerField(default=None, null=True)
