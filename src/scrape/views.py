from rest_framework import viewsets, status
from rest_framework.response import Response


from .models import ScrapeData
from .utils.scrape import start_scrape
from .serializers import ScrapeDataSerializers


class StartScrapeApiView(viewsets.ModelViewSet):
    http_method_names = ['get', 'head', 'post']
    serializer_class = ScrapeDataSerializers
    queryset = ScrapeData.objects.all()


    def create(self, request):
        total_pages = start_scrape()
        return Response({"message":f"Scraping started for {total_pages}."}, status=status.HTTP_201_CREATED)
    

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
