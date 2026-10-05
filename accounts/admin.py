from django.contrib import admin
from accounts.models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id','name','weight','height','gender','activity','goal')
    list_filter = ('gender',)
    search_fields = ('name',)