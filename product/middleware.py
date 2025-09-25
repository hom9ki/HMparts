from .models import SubCategory
from collections import defaultdict


def sc_context_processor(request):
    """Предварительная обработка контекста категорий для вывода в base.html"""

    sub_categories = SubCategory.objects.select_related('super_category').all().order_by('name')
    grouped_categories = defaultdict(list)
    for sub_category in sub_categories:
        if sub_category.super_category:
            grouped_categories[sub_category.super_category].append(sub_category)
        elif not sub_category.is_supercategory:
            grouped_categories[None].append(sub_category)

    context = {'categories': dict(grouped_categories)}
    return context
