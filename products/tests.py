from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from products.models import Category, Product
from django.urls import reverse


class ProductAPITest(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name='test')

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
