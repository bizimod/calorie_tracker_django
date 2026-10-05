from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='products'
    )

    calories = models.FloatField(help_text='ккал на 100 гр.')
    proteins = models.FloatField(help_text='белки на 100 гр.')
    fats = models.FloatField(help_text='жиры на 100 гр.')
    carbs = models.FloatField(help_text='углеводы на 100 гр.')

    barcode = models.CharField(max_length=100, blank=True, null=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'brand'],
                name='unique_product_name_brand'),
        ]

    def __str__(self):
        return f'{self.name} | {self.brand}' if self.brand else {self.name}

    # КБЖУ для порции в граммах
    def macros_for_weight(self, grams: float):
        k = grams / 100
        return {
            'calories': round(self.calories * k, 1),
            'proteins': round(self.proteins * k, 1),
            'fats': round(self.fats * k, 1),
            'carbs': round(self.carbs * k, 1),
        }
