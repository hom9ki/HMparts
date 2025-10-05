from itertools import chain

from django.contrib.postgres.search import SearchVector, SearchQuery
from django.db.models import Q

from ..models import Product, Set, HitProduct, HitSet
from garage.models import Model
from django.db import models


def search(query):
    """Полнотекстовый поиск"""
    if query:
        search_vector_product = SearchVector('title', weight='A') + SearchVector('content',
                                                                                 weight='B') + SearchVector(
            'applicability__model__name') + SearchVector('applicability__model__brand__name')
        search_vector_set = SearchVector('name', weight='A') + SearchVector('description',
                                                                            weight='B')

        products = Product.objects.annotate(
            search=search_vector_product, model_type=models.Value('product', output_field=models.CharField())).filter(
            Q(search=SearchQuery(query)))
        sets = Set.objects.annotate(
            search=search_vector_set, model_type=models.Value('product', output_field=models.CharField())).filter(
            Q(search=SearchQuery(query)))

    results = set(chain(products, sets))

    return results


def hits_search():
    hit_products = HitProduct.objects.select_related('product').all()
    hit_sets = HitSet.objects.select_related('set_object').all()
    hits = chain(hit_products, hit_sets)
    hits = sorted(hits, key=lambda x: x.created_at, reverse=True)
    print(type(hits))
    return hits
