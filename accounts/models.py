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
        default=ActivityLevel.SEDENTARY
    )
    goal = models.CharField(
        max_length=10,
        choices=Goal.choices,
        default=Goal.MAINTAIN
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
        return (today.year - self.birth_date.year -
                (today.month, today.day) < (self.birth_date.month,self.birth_date.day))
