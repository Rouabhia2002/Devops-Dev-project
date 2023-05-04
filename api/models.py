from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save


# Create your models here.
class client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    domaine = models.CharField(max_length=300)
    phone= models.IntegerField()
    type= models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class instance(models.Model):
    client = models.ForeignKey(client, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

