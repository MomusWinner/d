from  django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Role, Order, Product, Supplier, PickupPoint
from django.contrib.auth.admin import UserAdmin

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('full_name', 'role')
    list_filter = UserAdmin.list_filter + ('role',)
    search_fields = UserAdmin.search_fields + ('full_name', 'role')

    fieldsets = UserAdmin.fieldsets + (
        ('Additional info', {
            'fields': ('full_name', 'role'),
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional info', {
            'fields': ('email', 'full_name', 'role'),
        }),
    )


admin.site.register(Role)
admin.site.register(Order)
admin.site.register(Product)
admin.site.register(Supplier)
admin.site.register(PickupPoint)