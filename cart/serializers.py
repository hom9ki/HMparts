from rest_framework import serializers

from cart.models import CartItem


class CartItemSerializer(serializers.ModelSerializer):
    """
    Отвечает за 1 пункт корзины 1 человека:
    - создание позиции
    - инкремент количества
    - декремент количества
    - удаление товара из корзины
    """

    product_id = serializers.IntegerField(source="product.id", read_only=True)  # а зачем, если все равно передаешь product целиком?
    product_price = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = (
            "id",
            "user",
            "product",
            "product_id",
            "quantity",
            "product_price",
            "total_price",
        )

    def create(
        self, validated_data
    ):  # чет не пон, кажется переусложнено и не совсем корректно
        print(f"Validated data:{validated_data}")
        request = self.context["request"]
        product = validated_data["product"]
        quantity = validated_data["quantity"]
        lookup_kwargs = {}
        create_kwargs = {}

        try:
            if request.user.is_authenticated:
                lookup_kwargs = {"user": request.user, "product": product}
                create_kwargs = {
                    "user": request.user,
                    "product": product,
                    "quantity": quantity,
                }

            elif not request.session.session_key:
                request.session.create()  # А если сессия уже была?
                session_key = request.session.session_key
                lookup_kwargs = {"session_key": session_key, "product": product}
                create_kwargs = {
                    "session_key": session_key,
                    "product": product,
                    "quantity": quantity,
                }

            cart = CartItem.objects.get(**lookup_kwargs)

            cart.quantity += quantity
            if cart.quantity <= 0:
                print(f"Serializer < 0:{cart.quantity}")
                cart.delete()
                return CartItem(
                    id=None,
                    product=product,
                    quantity=0,
                    user=request.user if request.user.is_authenticated else None,
                    session_key=request.session.session_key
                    if not request.user.is_authenticated
                    else None,
                )
            else:
                print(f"Serializer > 0:{cart.quantity}")
                cart.save()
                return cart

        except CartItem.DoesNotExist:
            if quantity > 0:
                return CartItem.objects.create(**create_kwargs)

    def get_total_price(self, obj):
        return obj.product_price()

    def get_product_price(self, obj):
        return obj.product.price


class CartSerializer(serializers.Serializer):
    """
    отвечает за присвоение корзины пользователю, анонимному и не очень
    - под этот сериализатор реализовываем апи-вью с методом PUT
    - создает сессию, если ее нет
    - передает полностью всегда ВСЮ корзину, не важно какое было действие - это поможет избежать расхождений между фронтом и бэком, а также дергать всегда только 1 метод апи на все действия
    """
    items = CartItemSerializer(many=True)
    user_id = serializers.IntegerField()
    session_key = serializers.CharField(max_length=32)
