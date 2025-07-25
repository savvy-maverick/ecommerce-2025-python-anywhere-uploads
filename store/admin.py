from django.contrib import admin
from .models import Product,Customer,Order,Category, Profile
from django.contrib.auth.models import User

# Register your models here.

admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(Category)


# mix profile info and user info
class ProfileInline(admin.StackedInline):
    model = Profile

# extend User model
class UserAdmin(admin.ModelAdmin):
    model = User
    field = ['username', 'first_name', 'last_name', 'email', ]
    inlines = [ProfileInline]

# unregister the old way
admin.site.unregister(User)

# re-register the new way
admin.site.register(User, UserAdmin)
