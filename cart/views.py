from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from cart.models import Cart
from cart.serializers import CartSerializer
from product.models import Product


@api_view(['GET'])
def cart_list(request):
    carts = Cart.objects.filter(user=request.user)
    serializer = CartSerializer(carts, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def cart_add(request, product_slug):
    try:
        product = get_object_or_404(Product, slug=product_slug)
        quantity = request.data.get('quantity')
        if not request.user.is_authenticated and not request.session.session_key:
            request.session.create()

        data = {'product': product.id, 'quantity': quantity}

        serializer = CartSerializer(data=data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["DELETE"])
def cart_remove(request, product_slug):
    if request.method == "DELETE":
        if request.user.is_authenticated:
            cart = Cart.objects.get(user=request.user, product__slug=product_slug)
        else:
            cart = Cart.objects.get(
                session_key=request.session.session_key, product__slug=product_slug
            )
        cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def cart_change(request, product_slug):
    pass


def cart_detail(request):
    try:
        carts = Cart.objects.filter(user=request.user)
    except Exception as e:
        print(f"Error: {e}")
        carts = None
    if carts:
        return render(request, "user_cart.html", {"cart_items": carts})
    else:
        return render(request, "user_cart.html", {"carts": None})
