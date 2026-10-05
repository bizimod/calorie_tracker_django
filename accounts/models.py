from datetime import date

from django.db import models


class Profile(models.Model):
    class Gender(models.TextChoices):
        MALE = 'male', 'мужской'
        FEMALE = 'female', 'женский'

    class ActivityLevel(models.TextChoices):
        SEDENTARY = 'sedentary', 'Минимальная (сидячая)'
        LIGHT = 'light', 'Легкая (5000+ шагов в день)'
        MODERATE = 'moderate', 'Средняя (2-3 тренировки в неделю + 7000+ шагов в день)'
        ACTIVE = 'active', 'Высокая (3+ тренировки в неделю + 10000+ шагов в день)'
        VERY_ACTIVE = 'very_active', 'Очень высокая (физическая работа прим.Работа на стройке)'

    class Goal(models.TextChoices):
        LOSE = 'lose', 'Похудение'
        MAINTAIN = 'maintain', 'Поддержание'
        GAIN = 'gain', 'Набор веса'

    name = models.CharField(max_length=100)
    weight = models.PositiveIntegerField(default=0, null=True, blank=True)
    height = models.PositiveIntegerField(default=0, null=True, blank=True)
    birth_date = models.DateField(null=True)
    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        null=True, blank=True
    )
    activity = models.CharField(
        max_length=20,
        choices=ActivityLevel.choices,
        default=ActivityLevel.SEDENTARY,
        null=True, blank=True
    )
    goal = models.CharField(
        max_length=10,
        choices=Goal.choices,
        default=Goal.MAINTAIN,
        null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile : {self.name}"

    @property
    def age(self):
        if not self.birth_date:
            return None
        today = date.today()
        return (today.year - self.birth_date.year) - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day))

    # рассчет базового метаболизма основываясь на возраст, вес, рост
    def calculate_bmr(self):
        if not all([self.weight, self.height, self.birth_date, self.gender]):
            return None
        base = 10 * self.weight + 6.25 * self.height - 5 * self.age
        return base + 5 if self.gender == self.Gender.MALE else base - 161

    # рассчет расхода калорий с учетом активности
    def calculate_tdee(self):
        bmr = self.calculate_bmr()
        if bmr is None:
            return None
        factors = {
            self.ActivityLevel.SEDENTARY: 1.2,
            self.ActivityLevel.LIGHT: 1.375,
            self.ActivityLevel.MODERATE: 1.55,
            self.ActivityLevel.ACTIVE: 1.725,
            self.ActivityLevel.VERY_ACTIVE: 2,
        }
        factor = factors.get(self.activity,1.2)
        return bmr * factor

    # расчет КБЖУ в граммах
    def calculate_daily_targets(self):
        tdee = self.calculate_tdee()
        if tdee is None:
            return None
        adjustments = {
            self.Goal.LOSE: 0.8,
            self.Goal.MAINTAIN: 1.0,
            self.Goal.GAIN: 1.2,
        }

        adjustment = adjustments.get(self.activity,1)
        calories = tdee * adjustment

        proteins = self.weight * 2.0
        fats = self.weight * 0.9
        carbs = (calories - proteins * 4 - fats * 9) / 4

        return {
            'calories': round(calories),
            'proteins': round(proteins),
            'fats': round(fats),
            'carbs': round(carbs),
        }
