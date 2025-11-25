from itertools import chain

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from garage.models import Garage
from .models import Product, SuperCategory, SubCategory, Category, Set
from feedback.models import ProductReview, SetReview
from .middleware import sc_context_processor
from .utillities.search import search, hits_search
from .serializers import ProductDescriptionSerializer, SetSerializer, ReviewSerializer, ProductQuestionSerializer, \
    SetDescriptionSerializer, SetReviewSerializer, ProductSerializer, SetQuestionSerializer


def index(request):
    """Отображение главной страницы"""
    hits = hits_search()
    return render(request, 'index.html', {'hits': hits[:3]})


def hits(request):
    """Отображение страницы с хитами продаж"""
    hits = hits_search()
    return render(request, 'hit_list.html', {'hits': hits})


def supercategory(request):
    context = sc_context_processor(request)
    return render(request, 'supercategory_list.html', context)


def product_card(request, slug):
    if request.user.is_authenticated:
        product = Product.objects.select_related('category').prefetch_related('descriptions',
                                                                              'product_reviews',
                                                                              'product_questions',
                                                                              'additionalimage_set',
                                                                              'applicability__model').get(slug=slug)
        main_avto = Garage.objects.get(user=request.user)
        has_descriptions = product.descriptions.all().exists()
        has_reviews = product.product_reviews.all().exists()
        has_questions = product.product_questions.all().exists()
        has_set = product.sets.all().exists()
        try:
            applicability = [apply.name for apply in product.applicability.model.all()]
            user_cars = [a.car_model.name for a in main_avto.garage.all() if a.is_main]
            has_common = any(model in applicability for model in user_cars)
            main_avto = ''.join(user_cars)
        except Exception as e:
            print(f'Error: {e}')
            has_common = False
            main_avto = None
        return render(request, 'card.html', {'product': product,
                                             'has_descriptions': has_descriptions,
                                             'has_reviews': has_reviews,
                                             'has_questions': has_questions,
                                             'has_set': has_set,
                                             'has_common': has_common,
                                             'main_avto': main_avto})
    else:
        product = Product.objects.select_related('category').prefetch_related('descriptions',
                                                                              'product_reviews',
                                                                              'product_questions',
                                                                              'additionalimage_set',
                                                                              'applicability__model').get(slug=slug)
        has_descriptions = product.descriptions.all().exists()
        has_reviews = product.product_reviews.all().exists()
        has_questions = product.product_questions.all().exists()
        has_set = product.sets.all().exists()
        return render(request, 'card.html', {'product': product,
                                             'has_descriptions': has_descriptions,
                                             'has_reviews': has_reviews,
                                             'has_questions': has_questions,
                                             'has_set': has_set,
                                             })


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
        return render(request, 'mini_card.html', {'products': products, 'subcategory': subcategory})
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
        return render(request, 'mini_card.html', {'products': products})


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

    return render(request, 'mini_card.html', {'products': content})


@api_view()
def product_api(request, slug, action):
    product = get_object_or_404(Product, slug=slug)
    print(product, action)
    if action == 'descriptions':
        queryset = product.descriptions.filter(product=product)
        serializer = ProductDescriptionSerializer(queryset, many=True)
    elif action == 'reviews':
        reviews = ProductReview.objects.filter(product=product).select_related('user')
        serializer = ReviewSerializer(reviews, many=True)
    elif action == 'questions':
        questions = product.product_questions.select_related('user')
        serializer = ProductQuestionSerializer(questions, many=True)
        print(serializer.data)
    elif action == 'set':
        sets = product.sets.all()
        serializer = SetSerializer(sets, many=True)

    else:
        return Response({'error': 'Invalid action'}, status=400)

    return Response(serializer.data)


@api_view(['GET'])
def set_api(request, slug, action):
    set_product = get_object_or_404(Set, slug=slug)
    if action == 'descriptions':
        return Response({'description': set_product.description})
    elif action == 'reviews':
        reviews = SetReview.objects.filter(set=set_product).select_related('user')

        serializer = SetReviewSerializer(reviews, many=True)
    elif action == 'questions':
        questions = set_product.set_questions.select_related('user')
        serializer = SetQuestionSerializer(questions, many=True)
    elif action == 'set':
        products = set_product.products.all()
        print(products)
        serializer = ProductSerializer(products, many=True)
    else:
        return Response({'error': 'Invalid action'}, status=400)

    return Response(serializer.data)
