
from django.db import models




from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Question(models.Model):
    text = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="questions")

    def __str__(self):
        return self.text
        
class Indicator(models.Model):
    name = models.CharField(max_length=100)
    positive = models.TextField()
    negative = models.TextField()

    def __str__(self):
        return self.name