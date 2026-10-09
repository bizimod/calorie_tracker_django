from django.core.validators import MinValueValidator
from django.db import models
from accounts.models import Profile
from products.models import Product


class Meal(models.Model):
    class MealType(models.TextChoices):
        BREAKFAST = 'breakfast','завтрак'
        LUNCH = 'lunch','обед'
        DINNER = 'dinner','ужин'
        SNACK = 'snack','перекус'

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='meals'
    )
    date = models.DateField(db_index=True)
    meal_type = models.CharField(max_length=20, choices=MealType.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date','meal_type']
        # один завтрак у человека в день
        constraints = [
            models.UniqueConstraint(
                fields=['profile','date','meal_type'],
                name='unique_meal_per_profile_per_day'
            ),
        ]

    def __str__(self):
        return f'{self.get_meal_type_display()} - {self.date} {self.profile}'

    # сумма КБЖУ по всем позициям приема пищи
    def totals(self):
        total = self.items.aggregate(
            calories=models.Sum('calories'),
            proteins=models.Sum('proteins'),
            fats=models.Sum('fats'),
            carbs=models.Sum('carbs'),
        )
        return {k: round(v or 0,1) for k, v in total.items()}

class MealItem(models.Model):
    meal = models.ForeignKey(
        Meal,
        on_delete=models.CASCADE,
        related_name='items',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='meal_items',
    )
    weight_grams = models.FloatField(
        validators=[MinValueValidator(0.1)],
        help_text='вес порции в граммах'
    )
    # чтоб при изменении КБЖУ в таблице уже внесенные значения не поплыли
    calories = models.FloatField(editable=False,default=0)
    proteins = models.FloatField(editable=False,default=0)
    fats = models.FloatField(editable=False,default=0)
    carbs = models.FloatField(editable=False,default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.product.name} - {self.weight_grams} гр.'

    def save(self, *args, **kwargs):
        if self.product_id and self.weight_grams:
            macros = self.product.macros_for_weight(self.weight_grams)
            self.calories = macros['calories']
            self.proteins = macros['proteins']
            self.fats = macros['fats']
            self.carbs = macros['carbs']
        super().save(*args, **kwargs)