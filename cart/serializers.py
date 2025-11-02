from rest_framework import serializers

from cart.models import Cart


class CartSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    product_price = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'user', 'product', 'product_id', 'quantity', 'product_price', 'total_price')

    def create(self, validated_data):
        print(f'Validated data:{validated_data}')
        request = self.context['request']
        product = validated_data['product']
        quantity = validated_data['quantity']
        lookup_kwargs = None
        create_kwargs = None

        try:
            if request.user.is_authenticated:
                lookup_kwargs = {'user': request.user, 'product': product}
                create_kwargs = {'user': request.user, 'product': product, 'quantity': quantity}

            elif not request.session.session_key:
                request.session.create()
                session_key = request.session.session_key
                lookup_kwargs = {'session_key': session_key, 'product': product}
                create_kwargs = {'session_key': session_key, 'product': product, 'quantity': quantity}

            cart = Cart.objects.get(**lookup_kwargs)

            cart.quantity += quantity
            if cart.quantity <= 0:
                print(f'Serializer < 0:{cart.quantity}')
                cart.delete()
                return Cart(
                    id=None,
                    product=product,
                    quantity=0,
                    user=request.user if request.user.is_authenticated else None,
                    session_key=request.session.session_key if not request.user.is_authenticated else None)
            else:
                print(f'Serializer > 0:{cart.quantity}')
                cart.save()
                return cart

        except Cart.DoesNotExist:
            if quantity > 0:
                return Cart.objects.create(**create_kwargs)

    def get_total_price(self, obj):
        return obj.product_price()

    def get_product_price(self, obj):
        return obj.product.price
