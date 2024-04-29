from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name='name')
    slug = models.CharField(max_length=200, unique=True, verbose_name='slug')

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]

        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category,
                                 related_name='products',
                                 on_delete=models.CASCADE,
                                 verbose_name='category')
    name = models.CharField(max_length=200, verbose_name='name')
    slug = models.CharField(max_length=200, verbose_name='slug')
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True, verbose_name='image')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10,
                                decimal_places=2)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-name']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
            models.Index(fields=['-created'])
        ]

        verbose_name = 'product'
        verbose_name_plural = 'products'

    def __str__(self):
        return self.name
