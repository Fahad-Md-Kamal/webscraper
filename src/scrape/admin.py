from django.contrib import admin
from .models import ScrapeData


@admin.register(ScrapeData)
class ScrapeDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price')
    list_display_links = ('title',)
    search_fields = ('id', 'title')