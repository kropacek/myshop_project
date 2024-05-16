from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin
from django.utils.translation import get_language

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(TabbedTranslationAdmin):
    prepopulated_fields = {'slug_en': ('name_en',),
                           'slug_ru': ('name_ru',)}

    def get_list_display(self, request):
        if get_language() == 'en':
            list_display = ['name_en', 'slug_en']
        else:
            list_display = ['name_ru', 'slug_ru']
        return list_display


@admin.register(Product)
class ProductAdmin(TabbedTranslationAdmin):
    list_filter = ['available', 'created', 'updated']
    prepopulated_fields = {'slug_en': ('name_en',),
                           'slug_ru': ('name_ru',)}
    raw_id_fields = ['category']

    def get_list_display(self, request):
        if get_language() == 'en':
            list_display = ['name_en', 'slug_en', 'price', 'available', 'created', 'updated']
        else:
            list_display = ['name_ru', 'slug_ru', 'price', 'available', 'created', 'updated']

        self.list_editable = ['price', 'available']

        return list_display
