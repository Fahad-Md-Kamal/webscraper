from django.contrib import admin
from .models import ScrapeData


@admin.register(ScrapeData)
class ScrapeDataAdmin(admin.ModelAdmin):
    """Responsible for represengting the application for admin panel

    fields:
        list_dispaly : model fields that needs to be displayed in list
        list_display_links: model field that should be clickable on the list
        search_fields: on which filed the django admin panel will make the search
    """
    list_display = ('id', 'title', 'price')
    list_display_links = ('title',)
    search_fields = ('id', 'title')