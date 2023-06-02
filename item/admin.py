from django.contrib import admin

from .models import Category, Item

# Register models
admin.site.register(Category)
admin.site.register(Item)