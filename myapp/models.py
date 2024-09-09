from django.db import models
class Sequence(models.Model):
    individual = models.CharField(max_length=255)
    protein = models.CharField(max_length=255)
    aa_sequence = models.TextField()


    def set_aa_sequence(self, aa):
        self.aa_sequence = ','.join(aa)
    def get_aa_sequence(self):
        return self.aa_sequence.split(',')

    def get_individual(self):
        return self.individual
