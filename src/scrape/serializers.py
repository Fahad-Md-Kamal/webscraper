from rest_framework import serializers

from .models import ScrapeData

class ScrapeDataSerializers(serializers.ModelSerializer):

    class Meta:
        model = ScrapeData
        fields = '__all__'