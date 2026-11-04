from datetime import date

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from diary.models import Meal, MealItem
from products.models import Product

User = get_user_model()

DEMO = [
    ('Гречка отварная', 110, 4.2, 1.1, 21.3),
    ('Куриная грудка', 165, 31.0, 3.6, 0.0),
    ('Яйцо куриное', 155, 12.6, 10.6, 1.1),
    ('Овсянка на воде', 88, 3.0, 1.7, 15.0),
    ('Яблоко', 52, 0.3, 0.2, 14.0),
    ('Йогурт греческий', 80, 7.0, 2.0, 8.5),
]


class Command(BaseCommand):
    help = 'Создаёт демо-пользователя demo@example.com / demo12345 c заполненным днём'

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            email='demo@example.com', defaults={'username': 'demo'},
        )
        if created:
            user.set_password('demo12345')
            user.save()

        profile = user.profile
        profile.name = 'Демо'
        profile.weight, profile.height = 80, 175
        profile.gender, profile.activity, profile.goal = 'male', 'moderate', 'lose'
        profile.birth_date = date(2000, 8, 15)
        profile.save()

        products = []
        for name, kcal, p, f, c in DEMO:
            product, _ = Product.objects.get_or_create(
                name=name, brand='',
                defaults={'calories': kcal, 'proteins': p, 'fats': f, 'carbs': c},
            )
            products.append(product)

        today = timezone.localdate()

        meal_plans={
            'breakfast':products[3:],
            'lunch':products[0:2],
            'dinner':products[1:3],
        }

        for meal_type, meal_products in meal_plans.items():
            meal, _ = Meal.objects.get_or_create(
                profile=profile, date=today, meal_type=meal_type,
            )
            for product in meal_products:
                MealItem.objects.get_or_create(
                    meal=meal, product=product, defaults={'weight_grams': 100},
                )

        self.stdout.write(self.style.SUCCESS('Демо готово: demo@example.com / demo12345'))
