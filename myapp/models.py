from django.db import models

# Create your models here.
#Sraddha's code (superfluous given the amount of files, but still)

from django.core.validators import MinValueValidator


class PokemonType(models.Model):
    TYPE_CHOICES = [
        ('Fire', 'Fire'),
        ('Water', 'Water'),
        ('Grass', 'Grass'),
        ('Electric', 'Electric'),
        ('Normal', 'Normal'),
    ]

    name = models.CharField(max_length=20, choices=TYPE_CHOICES, unique=True)

    def __str__(self):
        return self.name


class DataRun(models.Model):
    SOURCE_CHOICES = [
        ('csv', 'CSV Import'),
        ('api', 'API Fetch'),
    ]

    source = models.CharField(max_length=10, choices=SOURCE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.source


class Pokemon(models.Model):
    name = models.CharField(max_length=100)

    primary_type = models.ForeignKey(PokemonType, on_delete=models.CASCADE)

    hp = models.IntegerField(validators=[MinValueValidator(1)])

    data_run = models.ForeignKey(DataRun, on_delete=models.CASCADE)

    class Meta:
        ordering = ['name']
        unique_together = ['name', 'primary_type']

    def __str__(self):
        return self.name



    
