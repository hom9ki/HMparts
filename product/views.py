from itertools import chain

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from .models import HitProduct, Product, SuperCategory, SubCategory, Category, Set, HitSet
from .middleware import sc_context_processor
from .utillities.search import search


def index(request):
    hit_products = HitProduct.objects.select_related('product').all()
    hit_sets = HitSet.objects.select_related('set_object').all()
    hits = chain(hit_products, hit_sets)
    hits = list(hits)
    hits.sort(key=lambda x: x.created_at, reverse=True)
    return render(request, 'index.html', {'hits': hits})


def supercategory(request):
    context = sc_context_processor(request)
    return render(request, 'supercategory_list.html', context)


def product_card(request, slug):
    product = Product.objects.select_related('category').prefetch_related('dynamic_descriptions', 'descriptions',
                                                                          'additionalimage_set').get(slug=slug)
    descriptions_data = {}
    for info in product.descriptions.all():
        if info.description_type not in descriptions_data:
            descriptions_data[info.description_type] = []
        items = info.content.split('-')
        descriptions_data[info.description_type].extend([item.strip() for item in items if item.strip()])
    return render(request, 'product_card.html', {'product': product,
                                                 'descriptions_data': descriptions_data})


def subcategory(request, slug):
    supercategory = get_object_or_404(SuperCategory, slug=slug)
    subcategories = SubCategory.objects.filter(super_category=supercategory).order_by('name')
    print(supercategory, subcategories)
    return render(request, 'subcategory_list.html', {'subcategories': subcategories,
                                                     'supercategory': supercategory})


def category(request, slug=None):
    if slug:
        subcategory = get_object_or_404(SubCategory, slug=slug)
        products = Product.objects.filter(category=subcategory).order_by('title')
        return render(request, 'product_list.html', {'products': products, 'subcategory': subcategory})
    else:
        all_categories = Category.objects.filter(Q(super_category=None) |
                                                 Q(is_supercategory=False, super_category=None)).order_by('name')
        return render(request, 'category_list.html', {'all_categories': all_categories})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    if category.is_supercategory:
        subcategory = SubCategory.objects.filter(super_category=category).order_by('name')
        return render(request, 'subcategory_list.html', {'subcategories': subcategory})
    else:
        products = Product.objects.filter(category=category).order_by('title')
        return render(request, 'product_list.html', {'products': products})


def set_all(request):
    sets = Set.objects.prefetch_related('set_products').all()
    return render(request, 'set_list.html', {'sets': sets})


def set_detail(request, slug):
    set_object = get_object_or_404(Set, slug=slug)
    if set_object:
        products = set_object.set_products.all()
        print(products)
        return render(request, 'set_detail.html', {'set_object': set_object, 'products': products})
    else:
        return render(request, '404.html', {'error': 'Set not found'})


def search_product_set(request):
    query = request.GET.get('q')
    results = search(query)
    return render(request, 'search.html', {'results': results,
                                           'query': query, })

def product_list(request):
    objects = Product.objects.all().order_by('title')
    p = Paginator(objects, 12)
    page = request.GET.get('page', 1)
    content = p.get_page(page)

    return render(request, 'product_list.html', {'products': content})
