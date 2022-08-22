from django.db import models

class ScrapeData(models.Model):
    """
    Responsible for storing Scrapped Data
    """
    product_uid = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    price = models.FloatField()
    image_src= models.URLField(null=True, blank=True)
    product_link=models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        """
        Responsible for representing object as human readable form.
        """
        return f'{self.title} - {self.price}'
