from django.db import models
class Sequence(models.Model):
    Accession = models.CharField(max_length=25)
    Variants = models.JSONField(default=dict)
    # Cohorts = models.JSONField(default=dict)
