from django.db import models
from base.models import TimestampedUUIDModel
from users.models import User


class Community(TimestampedUUIDModel):
    slug = models.CharField(max_length=256, unique=True)
    name = models.CharField(max_length=256)
    description = models.TextField(default="", null=True, blank=True)

    website = models.CharField(max_length=256, null=True, blank=True)
    opensea = models.CharField(max_length=256, null=True, blank=True)
    twitter = models.CharField(max_length=256, null=True, blank=True)
    discord = models.CharField(max_length=256, null=True, blank=True)
    etherscan = models.CharField(max_length=256, null=True, blank=True)


class Contract(TimestampedUUIDModel):
    address = models.CharField(max_length=256, unique=True)
    symbol = models.CharField(max_length=256, blank=True)
    contract_type = models.CharField(max_length=64, blank=True)
    community = models.OneToOneField(
        Community,
        on_delete=models.CASCADE,
        related_name="contract",
    )


class CommunalCanvas(TimestampedUUIDModel):
    image = models.JSONField(default=dict)
    community = models.OneToOneField(
        Community,
        on_delete=models.CASCADE,
        related_name="communal_canvas",
    )