from django.contrib import admin
from .models import Product
# Register your models here.

@admin.register(Product)
class BlogTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "type_name","product_character","product_preface","product_closing")
    ordering = ("id",)  # id positive order -id,negetive
