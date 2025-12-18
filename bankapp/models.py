from django.db import models

# Create your models here.
class reg(models.Model):
    accno=models.BigIntegerField(primary_key=True)
    name=models.CharField(max_length=100)
    password=models.CharField(max_length=15)
    amount=models.BigIntegerField()
    address=models.CharField(max_length=100)
    mobileno=models.BigIntegerField(max_length=10)
    active= models.BooleanField(default=True)