from modeltranslation.translator import register, TranslationOptions
from .models import Product, Category


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'slug', 'description')


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'slug')
