from django.db import models
class Sequence(models.Model):
    Individual = models.CharField(max_length=10)
    Accession = models.CharField(max_length=25)
    Sequence = models.CharField(max_length=35000)
    Variants = models.JSONField(default=dict)
