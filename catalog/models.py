from django.db import models
from django.db.models import Q


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    class Unit(models.TextChoices):
        PIECE = "piece", "piece"
        BAG = "bag", "bag"
        SHEET = "sheet", "sheet"
        TIN = "tin", "tin"
        ROLL = "roll", "roll"
        PACK = "pack", "pack"
        SET = "set", "set"
        KG = "kg", "kg"
        METRE = "metre", "metre"
        LITRE = "litre", "litre"

    # A category with products cannot be deleted. Deleting a brand keeps its products.
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    brand = models.ForeignKey(
        Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name="products"
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=20, choices=Unit.choices, default=Unit.PIECE)
    # KES, VAT-inclusive (assumption A1 in architecture.md).
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # Local names customers search with, e.g. "mabati saruji" (assumption A2).
    keywords = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    # PositiveIntegerField adds a database check, so stock cannot go below zero.
    stock_on_hand = models.PositiveIntegerField(default=0)
    low_stock_level = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(condition=Q(price__gt=0), name="product_price_positive"),
        ]

    def __str__(self):
        return self.name
