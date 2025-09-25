from itertools import chain

from django.contrib.postgres.search import SearchVector, SearchQuery
from ..models import Product, Set
from django.db import models


def search(query):
    """Полнотекстовый поиск"""
    if query:
        search_vector_product = SearchVector('title')
        search_vector_set = SearchVector('name')

        products = Product.objects.annotate(
            search=search_vector_product, model_type=models.Value('product', output_field=models.CharField())).filter(
            search=SearchQuery(query)
            )
        sets = Set.objects.annotate(
            search=search_vector_set, model_type=models.Value('product', output_field=models.CharField())).filter(
            search=SearchQuery(query)
            )
    print(products, sets)
    results = chain(products, sets)

    return results
