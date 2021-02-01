from django.db import models
from django.urls import reverse

# Create your models here.
class Metar(models.Model):
    siteID = models.TextField(max_length=5)
    Lat = models.DecimalField(decimal_places=2,max_digits=10)
    Lon = models.DecimalField(decimal_places=2,max_digits=100)
    Temp = models.DecimalField(decimal_places=2,max_digits=6,default=9999.99)

    def get_absolute_url(self):
        #return f"/Metar/{self.id}/"
        return reverse("metar_detail", kwargs={"id":self.id})