from django.db import models

# Create your models here.
class Greeting(models.Model):
    when = models.DateTimeField('date created', auto_now_add=True)

class Swatch(models.Model):
	name = models.CharField(max_length=500)
	red = models.IntegerField()
	green = models.IntegerField()
	blue = models.IntegerField()