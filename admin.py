from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model=User; list_display=('email','first_name','last_name','type','is_active','is_staff');ordering=('email',)
    fieldsets=UserAdmin.fieldsets + (('Дополнительно',{'fields':('company','position','type')}),)
