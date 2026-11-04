from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from diary.models import Meal, MealItem
from products.models import Product

User = get_user_model()

