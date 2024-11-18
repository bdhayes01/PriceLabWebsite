from django.db import models
class Sequence_and_CHalf(models.Model):
    Accession = models.CharField(max_length=25, unique=True)
    Variants = models.JSONField(default=dict)
    Sequence = models.CharField(max_length=35000, default=str)
    CHalf = models.JSONField(default=dict)
    # TODO: Add in C-half

class Metadata(models.Model):
    Individual = models.CharField(max_length=3)
    Age = models.IntegerField()
    Disease = models.BooleanField()
    Sex = models.BooleanField()
    Drug = models.BooleanField()
    BMI = models.FloatField()
