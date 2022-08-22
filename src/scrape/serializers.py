from rest_framework import serializers

from .models import ScrapeData

class ScrapeDataSerializers(serializers.ModelSerializer):
    """
    Responsible for Serializing Python format to Json format and vice-vasrsa
    """

    class Meta:
        model = ScrapeData
        fields = '__all__'