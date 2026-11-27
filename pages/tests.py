from django.contrib.auth.models import Group
from django.test import TestCase, override_settings
from django.urls import reverse


class HomePageTests(TestCase):
    def test_home_renders_base_template(self):
        response = self.client.get(reverse("pages:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "base.html")

    def test_skip_link_is_first_and_targets_main(self):
        html = self.client.get(reverse("pages:home")).content.decode()
        self.assertIn('href="#main"', html)
        self.assertIn('<main id="main"', html)
        self.assertLess(html.index('href="#main"'), html.index("<header"))

    def test_one_h1_and_shop_name(self):
        with override_settings(SHOP_NAME="Test Hardware"):
            html = self.client.get(reverse("pages:home")).content.decode()
        self.assertEqual(html.count("<h1"), 1)
        self.assertIn("Test Hardware", html)

    def test_links_built_css(self):
        html = self.client.get(reverse("pages:home")).content.decode()
        self.assertIn("/static/css/app.css", html)


class StaffGroupTests(TestCase):
    def test_groups_exist_after_migrate_with_no_permissions(self):
        for name in ("Shop owner", "Staff"):
            group = Group.objects.get(name=name)
            self.assertEqual(group.permissions.count(), 0)
