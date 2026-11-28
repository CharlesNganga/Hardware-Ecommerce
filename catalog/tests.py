from decimal import Decimal
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Brand, Category, Product


def make_product(category, **kwargs):
    defaults = {"name": "Claw hammer", "slug": "claw-hammer", "price": Decimal("850.00")}
    defaults.update(kwargs)
    return Product.objects.create(category=category, **defaults)


class ProductModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Hand tools", slug="hand-tools")

    def test_price_is_stored_as_exact_decimal(self):
        product = make_product(self.category, price=Decimal("1250.50"))
        product.refresh_from_db()
        self.assertEqual(product.price, Decimal("1250.50"))
        self.assertIsInstance(product.price, Decimal)

    def test_price_must_be_above_zero(self):
        for bad in (Decimal("0"), Decimal("-5.00")):
            with self.subTest(price=bad), self.assertRaises(IntegrityError), transaction.atomic():
                make_product(self.category, price=bad)

    def test_stock_cannot_be_negative(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            make_product(self.category, stock_on_hand=-1)

    def test_stock_can_be_zero(self):
        self.assertEqual(make_product(self.category, stock_on_hand=0).stock_on_hand, 0)

    def test_defaults(self):
        product = make_product(self.category)
        self.assertTrue(product.is_active)
        self.assertFalse(product.is_featured)
        self.assertEqual(product.low_stock_level, 5)
        self.assertEqual(product.unit, "piece")

    def test_slug_is_unique(self):
        make_product(self.category)
        with self.assertRaises(IntegrityError), transaction.atomic():
            make_product(self.category, name="Another")

    def test_category_with_products_cannot_be_deleted(self):
        make_product(self.category)
        with self.assertRaises(ProtectedError):
            self.category.delete()

    def test_deleting_a_brand_keeps_its_products(self):
        brand = Brand.objects.create(name="Acme", slug="acme")
        product = make_product(self.category, brand=brand)
        brand.delete()
        product.refresh_from_db()
        self.assertIsNone(product.brand)


class CatalogAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = get_user_model().objects.create_superuser("boss", "b@example.com", "pw")
        cls.category = Category.objects.create(name="Hand tools", slug="hand-tools")
        cls.product = make_product(cls.category, stock_on_hand=10)

    def setUp(self):
        self.client.force_login(self.admin_user)

    def test_changelists_load(self):
        for model in ("category", "brand", "product"):
            with self.subTest(model=model):
                response = self.client.get(reverse(f"admin:catalog_{model}_changelist"))
                self.assertEqual(response.status_code, 200)

    def test_product_search_finds_local_names(self):
        make_product(self.category, name="Roofing sheet", slug="roofing-sheet", keywords="mabati")
        url = reverse("admin:catalog_product_changelist")
        response = self.client.get(url, {"q": "mabati"})
        self.assertContains(response, "Roofing sheet")
        self.assertNotContains(response, "Claw hammer")

    def test_stock_is_editable_from_the_list(self):
        url = reverse("admin:catalog_product_changelist")
        response = self.client.post(
            url,
            {
                "form-TOTAL_FORMS": "1",
                "form-INITIAL_FORMS": "1",
                "form-MIN_NUM_FORMS": "0",
                "form-MAX_NUM_FORMS": "1000",
                "form-0-id": str(self.product.pk),
                "form-0-stock_on_hand": "7",
                "form-0-is_active": "on",
                "_save": "Save",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_on_hand, 7)


class SampleCatalogCommandTests(TestCase):
    def run_command(self):
        out = StringIO()
        call_command("load_sample_catalog", stdout=out)
        return out.getvalue()

    @override_settings(DEBUG=True)
    def test_loads_and_is_safe_to_run_twice(self):
        self.run_command()
        counts = (Category.objects.count(), Brand.objects.count(), Product.objects.count())
        self.run_command()
        self.assertEqual(
            counts, (Category.objects.count(), Brand.objects.count(), Product.objects.count())
        )
        self.assertGreater(counts[2], 0)
        self.assertTrue(Product.objects.filter(stock_on_hand=0).exists())

    @override_settings(DEBUG=False)
    def test_refuses_when_debug_is_off(self):
        with self.assertRaises(CommandError):
            self.run_command()
        self.assertEqual(Product.objects.count(), 0)
