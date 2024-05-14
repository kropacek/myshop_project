from django.conf import settings
from .models import Product
import redis


r = redis.Redis(host='redis',
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB)


class Recommender:

    def get_product_key(self, id):
        return f'product:{id}:purchased_with'

    def product_bought(self, products):
        products_ids = [p.id for p in products]

        for products_id in products_ids:
            for with_id in products_ids:

                if products_id != with_id:
                    r.zincrby(self.get_product_key(products_id),
                              1,
                              with_id)

    def suggest_products_for(self, products, max_result=6):

        products_ids = [p.id for p in products]

        if len(products_ids) == 1:

            suggestions = r.zrange(self.get_product_key(products_ids[0]),
                                   0, -1, desc=True)[:max_result]

        else:
            flat_ids = [str(id) for id in products_ids]
            tmp_key = f'tmp_{flat_ids}'

            keys = [self.get_product_key(id) for id in products_ids]
            # unite all scores and save united set into temporary key
            r.zunionstore(tmp_key, keys)
            # delete given products
            r.zrem(tmp_key, *products_ids)

            suggestions = r.zrange(tmp_key, 0, -1, desc=True)[:max_result]
            # delete temporary key
            r.delete(tmp_key)

        suggested_products_ids = [int(id) for id in suggestions]

        suggested_products = list(Product.objects.filter(id__in=suggested_products_ids))

        suggested_products.sort(key=lambda x: suggested_products_ids.index(x.id))

        return suggested_products

    def clear_purchases(self):
        for id in Product.objects.values_list('id', flat=True):
            r.delete(self.get_product_key(id))
