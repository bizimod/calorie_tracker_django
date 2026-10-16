import logging

from django.db import transaction
from django.core.cache import cache

from products.models import Product, Category
from .openfoodfacts import OpenFoodFactsClient, OpenFoodFactsError
from .normalizer import normalize_off_product

logger = logging.getLogger(__name__)


class ProductService:
    def __init__(self):
        self.client = OpenFoodFactsClient()

    def get_by_barcode(self, barcode: str) -> tuple[Product | None, bool]:
        """
        Возвращает (продукт, создан_ли_сейчас).
        1. Смотрим локально
        2. Если нет — идём в OFF
        3. Если OFF вернул — сохраняем к себе
        """
        # 1. Локально
        local = Product.objects.filter(barcode=barcode).first()
        if local:
            return local, False

        # 2. Внешний API
        try:
            raw = self.client.get_by_barcode(barcode)
        except OpenFoodFactsError:
            return None, False

        if not raw:
            return None, False

        normalized = normalize_off_product(raw)
        if not normalized:
            return None, False

        # 3. Сохраняем
        product = self._save_normalized(normalized)
        return product, product is not None

    def search_and_import(self, query: str, limit: int = 10) -> list[Product]:
        """
        1. Локальный поиск
        2. Поиск из OFF
        limit - максимальное количество продуктов,
                которое метод возвращает пользователю на экран
        """

        query = query.strip()
        if not query:
            return []

        # 1:
        local_qs = Product.objects.filter(name__icontains=query)[:limit]
        local = list(local_qs)

        if len(local) >= limit:
            return local

        # 2:
        try:
            raw_list = self.client.search(query, page_size=limit * 2)
        except OpenFoodFactsError:
            return local

        imported = []
        for raw in raw_list:
            normalized = normalize_off_product(raw)
            if not normalized:
                continue
            # Пропускаем дубликаты по штрихкоду
            if normalized['barcode'] and Product.objects.filter(
                    barcode=normalized['barcode']).exists():
                continue
            product = self._save_normalized(normalized)
            if product:
                imported.append(product)
            if len(local) + len(imported) >= limit:
                break

        return local + imported

    @transaction.atomic
    def _save_normalized(self, data: dict) -> Product | None:
        try:
            product = Product.objects.create(
                name=data['name'],
                brand=data.get('brand', ()),
                barcode = data.get('barcode', ()),
                calories = data['calories'],
                proteins = data['proteins'],
                fats = data['fats'],
                carbs = data['carbs'],
            )
            return product
        except Exception as e:
            logger.warning(f'Failed to save product {data.get('name')}: {e}')
            return None
