from django.contrib import admin

from accounts.models import Profile, User
from django.contrib.auth.admin import UserAdmin

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id','name','user','weight','height','gender','activity','goal')
    list_filter = ('gender',)
    search_fields = ('name',)
    autocomplete_fields = ('user',)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    ordering = ('email',)
    list_display = ('id','email','username','is_staff','is_active')
    search_fields = ('email','username',)
    fieldsets = UserAdmin.fieldsets + (('Профиль',{'fields':()}),)