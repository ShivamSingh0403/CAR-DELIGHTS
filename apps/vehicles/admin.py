from django.contrib import admin
from django.utils.html import format_html
from .models import Brand, Vehicle, VehicleVariant, VehicleImage, VehicleSpecification, VehicleCompatibility

class VehicleImageInline(admin.TabularInline):
    model = VehicleImage
    extra = 1
    fields = ('thumbnail_preview', 'image', 'image_type', 'is_primary', 'sort_order', 'source', 'license_status', 'license', 'license_url')
    readonly_fields = ('thumbnail_preview',)

    def thumbnail_preview(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" style="width: 60px; height: 40px; object-fit: cover; border-radius: 4px; border: 1px solid #444;" />', obj.get_image_url())
        return "No image"
    thumbnail_preview.short_description = "Preview"

class VehicleVariantInline(admin.TabularInline):
    model = VehicleVariant
    extra = 1

class VehicleSpecificationInline(admin.TabularInline):
    model = VehicleSpecification
    extra = 2

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'origin_country', 'is_featured', 'vehicle_count')
    list_filter = ('is_featured', 'origin_country')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

    def vehicle_count(self, obj):
        return obj.vehicles.count()
    vehicle_count.short_description = 'Total Models'

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_preview', 'full_name', 'brand', 'year', 'body_type', 'fuel_type', 'price', 'image_status_badge', 'is_3d_available', 'featured')
    list_filter = ('brand', 'body_type', 'fuel_type', 'transmission', 'is_3d_available', 'featured', 'year')
    search_fields = ('model', 'variant', 'brand__name', 'engine')
    prepopulated_fields = {'slug': ('model', 'variant', 'year')}
    inlines = [VehicleImageInline, VehicleVariantInline, VehicleSpecificationInline]
    actions = ['mark_as_featured', 'mark_3d_available']

    def thumbnail_preview(self, obj):
        return format_html('<img src="{}" style="width: 55px; height: 38px; object-fit: cover; border-radius: 4px;" />', obj.get_primary_image_url())
    thumbnail_preview.short_description = 'Asset'

    def image_status_badge(self, obj):
        if not obj.images.exists():
            return format_html('<span style="color: #EF4444; font-weight: bold;">MISSING</span>')
        primary = obj.primary_image
        if primary and primary.license_status == 'LICENSE_REQUIRED':
            return format_html('<span style="color: #F59E0B; font-weight: bold;">LICENSE REQUIRED</span>')
        return format_html('<span style="color: #10B981; font-weight: bold;">VALID</span>')
    image_status_badge.short_description = 'Image Status'

    def mark_as_featured(self, request, queryset):
        queryset.update(featured=True)
    mark_as_featured.short_description = "Mark selected vehicles as Featured"

    def mark_3d_available(self, request, queryset):
        queryset.update(is_3d_available=True)
    mark_3d_available.short_description = "Enable 3D Customizer for selected vehicles"

@admin.register(VehicleImage)
class VehicleImageAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_preview', 'vehicle', 'image_type', 'is_primary', 'license_status_badge', 'source', 'sort_order')
    list_filter = ('image_type', 'is_primary', 'license_status')
    search_fields = ('vehicle__model', 'vehicle__brand__name', 'alt_text', 'source')

    def thumbnail_preview(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" style="width: 60px; height: 40px; object-fit: cover; border-radius: 4px;" />', obj.get_image_url())
        return "No image"
    thumbnail_preview.short_description = "Preview"

    def license_status_badge(self, obj):
        colors = {'VALID': '#10B981', 'LICENSE_REQUIRED': '#EF4444', 'PROPRIETARY': '#38BDF8', 'EDITORIAL': '#F59E0B'}
        col = colors.get(obj.license_status, '#94A3B8')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', col, obj.get_license_status_display())
    license_status_badge.short_description = "License Status"

@admin.register(VehicleSpecification)
class VehicleSpecificationAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'category', 'key', 'value')
    list_filter = ('category',)
    search_fields = ('vehicle__model', 'key', 'value')

@admin.register(VehicleCompatibility)
class VehicleCompatibilityAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'category_slug', 'notes')
    search_fields = ('vehicle__model', 'category_slug')
