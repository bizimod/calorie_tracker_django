from django.db import models


class Profile(models.Model):
    class Gender(models.TextChoices):
        MALE = 'male','мужской'
        FEMALE = 'female','женский'

    name = models.CharField(max_length=100)
    weight = models.PositiveIntegerField(default=0, null=True, blank=True)
    height = models.PositiveIntegerField(default=0, null=True, blank=True)
    birth_date = models.DateField(null=True)
    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile : {self.name}"