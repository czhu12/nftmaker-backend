from django.db import models
from base.models import TimestampedUUIDModel
from users.models import User


class Project(TimestampedUUIDModel):
    name = models.CharField(max_length=256)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Group(TimestampedUUIDModel):
    name = models.CharField(max_length=256)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class Layer(TimestampedUUIDModel):
    name = models.CharField(max_length=256)
    order = models.IntegerField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    rarity = models.IntegerField(default=100)


class Asset(TimestampedUUIDModel):
    name = models.CharField(max_length=256)
    image_file = models.FileField(upload_to='uploads/', default=None)
    rarity = models.IntegerField()
    layer = models.ForeignKey(Layer, on_delete=models.CASCADE)
