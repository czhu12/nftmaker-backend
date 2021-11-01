from django.utils.translation import gettext_lazy as _
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

    class ContractType(models.TextChoices):
        ERC20 = 'ERC20', _('ERC20')
        ERC721 = 'ERC721', _('ERC721')
        ERC1155 = 'ERC1155', _('ERC1155')

    address = models.CharField(max_length=256, unique=True)
    symbol = models.CharField(max_length=256, blank=True)
    block_number = models.IntegerField(default=0)
    balance = models.BigIntegerField(default=0)
    contract_type = models.CharField(max_length=64, blank=True, choices=ContractType.choices)
    community = models.OneToOneField(
        Community,
        on_delete=models.CASCADE,
        related_name="contract",
        null=True,
        blank=True,
    )


class CommunalCanvas(TimestampedUUIDModel):
    image = models.JSONField(default=dict)
    community = models.OneToOneField(
        Community,
        on_delete=models.CASCADE,
        related_name="communal_canvas",
    )