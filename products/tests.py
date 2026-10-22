from datetime import date

from django.test import TestCase
import responses
from rest_framework.test import APITestCase

from products.models import Category, Product
from products.services.product_service import ProductService
from django.urls import reverse

from django.contrib.auth import get_user_model
User = get_user_model()


class ProductAPITest(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name='test')
        self.user = User.objects.create_user(
            email='test@test.com', username='test', password='pass123'
        )
        self.client.force_authenticate(user=self.user)

        # профиль создался автоматически сигналом
        self.profile = self.user.profile
        self.profile.weight = 80
        self.profile.height = 180
        self.profile.birth_date = date(2000, 1, 1)
        self.profile.gender = 'male'
        self.profile.activity_level = 'moderate'
        self.profile.goal = 'maintain'
        self.profile.save()

    def test_create_product(self):
        url = reverse('product-list')
        data = {
            'name': 'test', 'brand': 'test2',
            'category': self.category.id,
            'calories': 100, 'proteins': 10.2,
            'fats': 5.2, 'carbs': 50.2,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 1)

    def test_search_product(self):
        url = reverse('product-list') + '?search=Рис'
        Product.objects.create(
            name='Рис', calories=100, proteins=10,
            fats=5, carbs=50
        )
        Product.objects.create(
            name='Гречка', calories=110, proteins=10,
            fats=55, carbs=50
        )
        response = self.client.get(url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Рис')

    def test_macros_for_weight(self):
        p = Product.objects.create(
            name='Тест', calories=100, proteins=10,
            fats=5, carbs=20
        )
        result = p.macros_for_weight(150)
        self.assertEqual(result['calories'], 150.0)
        self.assertEqual(result['proteins'], 15.0)
        self.assertEqual(result['fats'], 7.5)
        self.assertEqual(result['carbs'], 30.0)

class OpenFoodFactsIntegrationTest(TestCase):

    @responses.activate
    def test_get_by_barcode_imports_product(self):
        barcode = '6111246721261'
        responses.add(
            responses.GET,
            f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json",
            json={
                'status': 1,
                'product': {
                    'code': barcode,
                    'product_name': 'Fromage Blanc Nature',
                    'brands': 'Milky Food Professional',
                    'nutriments': {
                        'energy-kcal_100g': 80.6,
                        'proteins_100g': 7.3,
                        'fat_100g': 12,
                        'carbohydrates_100g': 6.1,
                    },
                },
            },
            status=200,
        )

        service = ProductService()
        product, created = service.get_by_barcode(barcode)

        self.assertIsNotNone(product)
        self.assertTrue(created)
        self.assertEqual(product.name, 'Fromage Blanc Nature')
        self.assertEqual(product.calories, 80.6)

    @responses.activate
    def test_get_by_barcode_uses_local_first(self):
        Product.objects.create(
            name='Локальный', barcode='123',
            calories=100, proteins=1, fats=1, carbs=1,
        )
        # Никаких моков — если пойдёт в сеть, тест упадёт
        service = ProductService()
        product, created = service.get_by_barcode('123')

        self.assertIsNotNone(product)
        self.assertFalse(created)  # локально, значит не создавали
        self.assertEqual(product.name, 'Локальный')

    @responses.activate
    def test_barcode_endpoint(self):
        barcode = '4600000000000'
        responses.add(
            responses.GET,
            f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json",
            json={
                'status': 1,
                'product': {
                    'code': barcode,
                    'product_name': 'Тест',
                    'nutriments': {'energy-kcal_100g': 200},
                },
            },
        )
        url = reverse('product-by-barcode', kwargs={'code': barcode})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 201)  # импортирован
        self.assertEqual(response.data['name'], 'Тест')

    @responses.activate
    def test_barcode_not_found(self):
        barcode = '0000000000000'
        responses.add(
            responses.GET,
            f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json",
            json={'status': 0},
        )
        url = reverse('product-by-barcode', kwargs={'code': barcode})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)


class NormalizerTest(TestCase):
    def test_normalize_full_data(self):
        from products.services.normalizer import normalize_off_product
        raw = {
            'product_name': 'Йогурт',
            'brands': 'Danone, Activia',
            'code': '123',
            'nutriments': {
                'energy-kcal_100g': 60,
                'proteins_100g': 3.5,
                'fat_100g': 3.2,
                'carbohydrates_100g': 4.5,
            },
        }
        result = normalize_off_product(raw)
        self.assertEqual(result['name'], 'Йогурт')
        self.assertEqual(result['brand'], 'Danone')  # первый бренд
        self.assertEqual(result['calories'], 60.0)

    def test_normalize_computes_calories_from_macros(self):
        from products.services.normalizer import normalize_off_product
        raw = {
            'product_name': 'X',
            'nutriments': {
                'proteins_100g': 10,
                'fat_100g': 5,
                'carbohydrates_100g': 20,
                # energy-kcal отсутствует
            },
        }
        result = normalize_off_product(raw)
        # 10*4 + 5*9 + 20*4 = 40 + 45 + 80 = 165
        self.assertEqual(result['calories'], 165)

    def test_normalize_returns_none_if_no_nutrition(self):
        from products.services.normalizer import normalize_off_product
        result = normalize_off_product({'product_name': 'Пусто', 'nutriments': {}})
        self.assertIsNone(result)