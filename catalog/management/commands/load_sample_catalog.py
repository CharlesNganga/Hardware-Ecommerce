from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from catalog.models import Brand, Category, Product

# Invented placeholder data for development. Not the shop's real catalog.
CATEGORIES = ["Hand tools", "Plumbing", "Building materials", "Paint and finishes", "Fasteners"]
BRANDS = ["Sample Brand A", "Sample Brand B", "Sample Brand C"]
# name, category, brand, unit, price, keywords, stock, featured
PRODUCTS = [
    ("Claw hammer 16 oz", "Hand tools", "Sample Brand A", "piece", "850.00", "nyundo", 24, True),
    ("Spirit level 600 mm", "Hand tools", "Sample Brand A", "piece", "1100.00", "", 9, False),
    ("PVC pipe 1/2 in, 3 m", "Plumbing", "Sample Brand B", "piece", "420.00", "bomba", 60, True),
    ("Cement 50 kg", "Building materials", "Sample Brand C", "bag", "780.00", "saruji", 4, True),
    ("Roofing sheet 3 m", "Building materials", None, "sheet", "1450.00", "mabati", 40, False),
    (
        "Wall paint 4 L, white",
        "Paint and finishes",
        "Sample Brand B",
        "tin",
        "2300.00",
        "rangi",
        15,
        True,
    ),
    ("Padlock 50 mm", "Fasteners", "Sample Brand C", "piece", "650.00", "kufuli", 0, False),
    ("Wire nails 3 in", "Fasteners", None, "kg", "190.00", "misumari", 100, False),
]


def slugify(text):
    from django.utils.text import slugify as django_slugify

    return django_slugify(text)


class Command(BaseCommand):
    help = "Load invented sample categories, brands and products (development only)."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Refusing to load sample data while DEBUG is off.")

        categories = {
            name: Category.objects.update_or_create(name=name, defaults={"slug": slugify(name)})[0]
            for name in CATEGORIES
        }
        brands = {
            name: Brand.objects.update_or_create(name=name, defaults={"slug": slugify(name)})[0]
            for name in BRANDS
        }
        for name, category, brand, unit, price, keywords, stock, featured in PRODUCTS:
            Product.objects.update_or_create(
                slug=slugify(name),
                defaults={
                    "name": name,
                    "category": categories[category],
                    "brand": brands.get(brand),
                    "unit": unit,
                    "price": Decimal(price),
                    "keywords": keywords,
                    "stock_on_hand": stock,
                    "is_featured": featured,
                    "description": "Sample item for development.",
                },
            )
        self.stdout.write(
            f"Sample catalog ready: {len(categories)} categories, {len(brands)} brands, "
            f"{len(PRODUCTS)} products."
        )
