from django.contrib import admin
from .models import Truck, Driver, Job, AuditLog


from django.utils.html import format_html


@admin.register(Truck)
class TruckAdmin(admin.ModelAdmin):
    list_display = ('registration_no', 'capacity', 'status', 'photo_preview')
    list_filter = ('status',)
    search_fields = ('registration_no',)
    search_help_text = 'Search by registration number'
    fields = ('registration_no', 'capacity', 'status', 'photo')
    list_per_page = 25

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="height: 35px; width: 35px; object-fit: cover; border-radius: 4px;" loading="lazy" />', obj.photo.url)
        return "No photo"
    photo_preview.short_description = "Photo"


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('name', 'license_no', 'phone_no', 'user', 'photo_preview')
    list_filter = ('user__is_active',)
    search_fields = ('name', 'license_no', 'phone_no', 'user__username')
    search_help_text = 'Search by driver name, license number, phone, or linked username'
    fields = ('name', 'license_no', 'phone_no', 'user', 'photo')
    list_per_page = 25

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="height: 35px; width: 35px; object-fit: cover; border-radius: 4px;" loading="lazy" />', obj.photo.url)
        return "No photo"
    photo_preview.short_description = "Photo"


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('id', 'pick_up_location', 'delivery_location', 'status', 'assigned_truck', 'assigned_driver', 'created_at')
    list_filter = ('status',)
    search_fields = ('pick_up_location', 'delivery_location', 'cargo')
    search_help_text = 'Search by pickup, delivery, or cargo details'
    readonly_fields = ('created_at', 'modified_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_per_page = 25


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """AuditLog is read-only in admin to preserve the audit trail."""
    list_display = ('timestamp', 'user', 'action')
    list_filter = ('user',)
    search_fields = ('user', 'action')
    search_help_text = 'Search by username or audit action'
    readonly_fields = ('timestamp', 'user', 'action')
    date_hierarchy = 'timestamp'
    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

