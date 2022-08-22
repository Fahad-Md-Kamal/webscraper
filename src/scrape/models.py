from django.db import models

class ScrapeData(models.Model):
    title = models.CharField(max_length=255)
    price = models.FloatField()
    image_src= models.URLField(null=True, blank=True)
    product_link=models.URLField()

    def __str__(self) -> str:
        return f'{self.title} - {self.price}'
