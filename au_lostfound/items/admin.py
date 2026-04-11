from django.contrib import admin
from .models import Item, Complaint

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display  = ("item_name", "status", "submission_type", "submitted_at")
    list_filter   = ("status", "submission_type")
    search_fields = ("item_name", "description")

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display    = ('id', 'name', 'enrollment_number', 'user_email', 'category', 'submitted_by', 'status', 'created_at')
    list_filter     = ('status', 'category', 'created_at')
    search_fields   = ('name', 'enrollment_number', 'user_email', 'submitted_by__username', 'submitted_by__email')
    readonly_fields = ('submitted_by', 'created_at', 'updated_at')
    ordering        = ('-created_at',)
    fieldsets = (
        ('Student Information', {
            'fields': ('submitted_by', 'name', 'user_email', 'enrollment_number')
        }),
        ('Complaint Info', {
            'fields': ('category', 'subject', 'related_item')
        }),
        ('Resolution', {
            'fields': ('status', 'staff_remarks')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )