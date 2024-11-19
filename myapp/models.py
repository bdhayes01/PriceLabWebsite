from django.db import models
class Sequence(models.Model):
    Accession = models.CharField(max_length=25, unique=True)
    Variants = models.JSONField(default=dict)
    Sequence = models.CharField(max_length=35000, default=str)

class Metadata(models.Model):
    Individual = models.CharField(max_length=3)
    Age = models.IntegerField()
    Disease = models.BooleanField()
    Sex = models.BooleanField()
    Drug = models.BooleanField()
    BMI = models.FloatField()

class CHalf(models.Model):
    Accession = models.CharField(max_length=25, unique=True)
    CHalf = models.JSONField(default=dict)
