from django.contrib import admin

from .models import Brand, Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "category",
        "brand",
        "price",
        "unit",
        "stock_on_hand",
        "is_active",
        "is_featured",
    ]
    # Staff correct stock, and switch products on or off, straight from the list.
    list_editable = ["stock_on_hand", "is_active", "is_featured"]
    list_filter = ["is_active", "is_featured", "category", "brand"]
    list_select_related = ["category", "brand"]
    search_fields = ["name", "keywords", "brand__name"]
    prepopulated_fields = {"slug": ("name",)}
    list_per_page = 50
