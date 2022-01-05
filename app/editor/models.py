from django.db import models
from base.models import TimestampedUUIDModel
from users.models import User
from community.models import Contract


class Project(TimestampedUUIDModel):
    name = models.CharField(max_length=256)
    description = models.TextField(default="", null=True, blank=True)

    website = models.CharField(max_length=256, null=True, blank=True)
    opensea = models.CharField(max_length=256, null=True, blank=True)
    twitter = models.CharField(max_length=256, null=True, blank=True)
    discord = models.CharField(max_length=256, null=True, blank=True)
    etherscan = models.CharField(max_length=256, null=True, blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    ispublic = models.BooleanField(default=False)
    listed = models.BooleanField(default=False)
    width = models.IntegerField(default=512)
    height = models.IntegerField(default=512)

    contract = models.OneToOneField(
        Contract,
        on_delete=models.CASCADE,
        related_name="project",
        null=True,
        blank=True,
    )


class Group(TimestampedUUIDModel):
    name = models.CharField(max_length=256)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="groups")


class Layer(TimestampedUUIDModel):
    name = models.CharField(max_length=256)
    order = models.IntegerField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="layers")
    rarity = models.IntegerField(default=100)


class Asset(TimestampedUUIDModel):
    name = models.CharField(max_length=256)
    image_file = models.FileField(upload_to='uploads/', default=None)
    rarity = models.IntegerField()
    layer = models.ForeignKey(Layer, on_delete=models.CASCADE, related_name="assets")
