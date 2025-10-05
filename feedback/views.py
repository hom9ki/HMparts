from rest_framework.decorators import api_view
from rest_framework.response import Response

from feedback.models import ProductReview
from .serializers import ProductReviewSerializer
from product.models import Product


def feedback(request):
    pass


def answer(request, slug):
    pass


@api_view(['POST'])
def add_review(request, slug):
    if request.method == 'POST':
        product = Product.objects.get(slug=slug)

        if ProductReview.objects.filter(user=request.user, product=product).exists():
            return Response({
                "error": "Вы уже оставляли отзыв на этот товар"
            }, status=400)

        review_data = {
            "user": request.user.id,
            "product": product.id,
            "text": request.data.get('text'),

        }
        serializer = ProductReviewSerializer(data=review_data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
