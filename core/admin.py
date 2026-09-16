from django.contrib import admin
from .models import Truck, Driver, Job, AuditLog


@admin.register(Truck)
class TruckAdmin(admin.ModelAdmin):
    list_display = ('registration_no', 'capacity', 'status')
    list_filter = ('status',)
    search_fields = ('registration_no',)


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('name', 'license_no', 'phone_no')
    search_fields = ('name', 'license_no')


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('id', 'pick_up_location', 'delivery_location', 'status', 'assigned_truck', 'assigned_driver', 'created_at')
    list_filter = ('status',)
    search_fields = ('pick_up_location', 'delivery_location', 'cargo')
    readonly_fields = ('created_at', 'modified_at')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """AuditLog is read-only in admin to preserve the audit trail."""
    list_display = ('timestamp', 'user', 'action')
    list_filter = ('user',)
    search_fields = ('user', 'action')
    readonly_fields = ('timestamp', 'user', 'action')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
