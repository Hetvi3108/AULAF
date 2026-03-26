from django.contrib import admin
from .models import Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):

    # Show correct fields in admin panel
    list_display = ("item_name", "status", "submission_type", "submitted_at")

    # Filter by status and submission type
    list_filter = ("status", "submission_type")

    # Search by item name
    search_fields = ("item_name","description")
