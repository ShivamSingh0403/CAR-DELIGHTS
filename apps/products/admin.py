from django.contrib import admin
from django.utils.html import format_html
from .models import Category, ProductBrand, Product, ProductImage, ProductSpecification, ProductCompatibility

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('thumbnail_preview', 'image', 'image_type', 'sort_order', 'installed_vehicle', 'source', 'license_status', 'license_info')
    readonly_fields = ('thumbnail_preview',)
    autocomplete_fields = ['installed_vehicle']

    def thumbnail_preview(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" style="width: 55px; height: 38px; object-fit: cover; border-radius: 4px; border: 1px solid #444;" />', obj.get_image_url())
        return "No image"
    thumbnail_preview.short_description = "Preview"

class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1

class ProductCompatibilityInline(admin.TabularInline):
    model = ProductCompatibility
    extra = 1
    autocomplete_fields = ['vehicle']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug', 'is_featured', 'product_count')
    list_filter = ('is_featured', 'parent')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Total Products'

@admin.register(ProductBrand)
class ProductBrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'origin_country', 'product_count')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

    def product_count(self, obj):
        return obj.products.count()

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_preview', 'name', 'category', 'brand', 'price', 'mrp', 'image_status_badge', 'stock', 'rating', 'featured', 'is_active')
    list_filter = ('category', 'brand', 'featured', 'is_active', 'is_universal', 'is_3d_part', 'part_type')
    search_fields = ('name', 'sku', 'description', 'brand__name')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductSpecificationInline, ProductCompatibilityInline]
    actions = ['mark_as_featured', 'activate_products', 'deactivate_products']

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

    def activate_products(self, request, queryset):
        queryset.update(is_active=True)

    def deactivate_products(self, request, queryset):
        queryset.update(is_active=False)

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_preview', 'product', 'image_type', 'license_status_badge', 'installed_vehicle', 'source', 'sort_order')
    list_filter = ('image_type', 'license_status')
    search_fields = ('product__name', 'alt_text', 'source')
    autocomplete_fields = ['product', 'installed_vehicle']

    def thumbnail_preview(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" style="width: 55px; height: 38px; object-fit: cover; border-radius: 4px;" />', obj.get_image_url())
        return "No image"
    thumbnail_preview.short_description = "Preview"

    def license_status_badge(self, obj):
        colors = {'VALID': '#10B981', 'LICENSE_REQUIRED': '#EF4444', 'PROPRIETARY': '#38BDF8', 'EDITORIAL': '#F59E0B'}
        col = colors.get(obj.license_status, '#94A3B8')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', col, obj.get_license_status_display())
    license_status_badge.short_description = "License Status"

@admin.register(ProductCompatibility)
class ProductCompatibilityAdmin(admin.ModelAdmin):
    list_display = ('product', 'vehicle', 'variant_notes')
    search_fields = ('product__name', 'vehicle__model', 'vehicle__brand__name')
    autocomplete_fields = ['product', 'vehicle']
