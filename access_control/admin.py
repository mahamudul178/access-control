"""
access_control/admin.py
Register the AccessLog model in the Django Admin Panel
"""

from django.contrib import admin
from .models import AccessLog


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    """
    Admin interface customization for AccessLog
    """

    # Fields to display in the list view
    list_display = ('id', 'card_id', 'door_name', 'access_granted', 'timestamp')

    # Filters in the sidebar
    list_filter = ('access_granted', 'door_name', 'timestamp')

    # Search functionality
    search_fields = ('card_id', 'door_name')

    # Read-only fields (cannot be edited)
    readonly_fields = ('timestamp', 'created_at', 'id')

    # Field grouping in the detail view
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'card_id', 'door_name', 'access_granted')
        }),
        ('Time Information', {
            'fields': ('timestamp', 'created_at'),
            'classes': ('collapse',)  # Collapsible section
        }),
    )

    # Editable fields directly from the list page
    list_editable = ('access_granted',)

    # Number of items per page
    list_per_page = 20

    # Ordering (latest first)
    ordering = ('-timestamp',)

    def save_model(self, request, obj, form, change):
        """
        Called when an object is saved from the admin panel
        """
        super().save_model(request, obj, form, change)

        # Optional: log to console
        if change:
            print(f"✓ AccessLog updated: {obj.card_id} - {obj.door_name}")
        else:
            print(f"✓ AccessLog created: {obj.card_id} - {obj.door_name}")

    def delete_model(self, request, obj):
        """
        Called when an object is deleted from the admin panel
        """
        card_id = obj.card_id
        door_name = obj.door_name
        super().delete_model(request, obj)
        print(f"✓ AccessLog deleted: {card_id} - {door_name}")

    # Custom admin actions
    actions = ['mark_as_granted', 'mark_as_denied']

    def mark_as_granted(self, request, queryset):
        """
        Mark selected logs as GRANTED
        """
        updated = queryset.update(access_granted=True)
        self.message_user(
            request,
            f"{updated} log(s) have been marked as GRANTED."
        )
    mark_as_granted.short_description = "Mark selected entries as GRANTED"

    def mark_as_denied(self, request, queryset):
        """
        Mark selected logs as DENIED
        """
        updated = queryset.update(access_granted=False)
        self.message_user(
            request,
            f"{updated} log(s) have been marked as DENIED."
        )
    mark_as_denied.short_description = "Mark selected entries as DENIED"
