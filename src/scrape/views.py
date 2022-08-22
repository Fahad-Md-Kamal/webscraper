from rest_framework import viewsets
from rest_framework.response import Response


from .models import ScrapeData
from .utils.scrape import get_product_data
from .serializers import ScrapeDataSerializers


class StartScrapeApiView(viewsets.ModelViewSet):
    http_method_names = ['get', 'head', 'post']
    serializer_class = ScrapeDataSerializers
    queryset = ScrapeData.objects.all()


    def create(self, request):
        total = get_product_data()
        return Response({"message":f"Total {total} products scrapped."}, status=200)
    

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
