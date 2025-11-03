from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Location(models.Model):
    name = models.CharField(max_length=100, null=True)
    zone = models.CharField(max_length=100, null=True)
    state = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=100, null=True)
    entryprice = models.IntegerField(default=0)
    description = models.TextField()

    def __str__(self):
        return self.name

class Liked(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.description:
            self.description = self.location.description
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} liked {self.location.name}"


class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recommended_locations = models.ManyToManyField(Location)
    timestamp = models.DateTimeField(auto_now=True)