from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Garage, UserCar, Brand, Model
from django.contrib import messages
from .forms import AddCarForm
from .serializers import UserCarSerializer, BrandSerializer, ModelSerializer


@login_required
def garage_list(request):
    if request.user.is_authenticated:
        auto_list = Garage.objects.filter(user=request.user)
        return render(request, 'garage.html', {'garage': auto_list})
    else:
        return redirect('login')


@login_required
def delete_car(request, car_id):
    car = get_object_or_404(UserCar, id=car_id)
    print(car)
    if request.method == 'POST':
        car.delete()
        return redirect('garage:garage')

    else:
        return redirect('garage:garage')


@login_required
def add_car(request):
    garage, created = Garage.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = AddCarForm(request.POST)
        if form.is_valid():
            car_model = form.cleaned_data['car_model']
            is_main = form.cleaned_data['is_main']

            if UserCar.objects.filter(garage=garage, car_model=car_model).exists():
                messages.error(request, f'{car_model} уже есть в списке')
                return redirect('garage:garage')

            if is_main:
                UserCar.objects.filter(garage=garage).update(is_main=False)

            user_car = form.save(commit=False)
            user_car.garage = garage
            user_car.save()

            messages.success(request, f'Автомобиль {car_model} успешно добавлен')
            return redirect('garage:garage')
    else:
        form = AddCarForm()
    return render(request, 'add_car.html', {'form': form})


@api_view(['POST'])
def api_user_car(request):
    if request.method == 'POST':
        garage, created = Garage.objects.get_or_create(user=request.user)
        car_data = request.data.copy()
        car_data['garage'] = garage.id

        serializer = UserCarSerializer(data=car_data)
        if serializer.is_valid():
            if car_data.get('is_main'):
                UserCar.objects.filter(garage=garage).update(is_main=False)
                serializer.save(garage=garage)
                return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def api_user_garage_detail(request, pk):
    user_car = get_object_or_404(UserCar, pk=pk, garage__user=request.user)
    print(user_car)
    if request.method == 'GET':
        serializer = UserCarSerializer(user_car)
        return Response(serializer.data)
    elif request.method == 'PUT' or request.method == 'PATCH':
        print(request.data)
        if request.data.get('is_main'):
            UserCar.objects.filter(garage=user_car.garage).update(is_main=False)
            serializer = UserCarSerializer(instance=user_car, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
    elif request.method == 'DELETE':
        user_car.delete()
    return Response(status=204)


@api_view(['GET'])
def api_brand_list(request):
    brand_list = Brand.objects.all()
    serializer = BrandSerializer(brand_list, many=True)
    return Response(serializer.data)


def api_model_list(request):
    brand_id = request.GET.get('brand_id')
    models = Model.objects.filter(brand_id=int(brand_id))

    brand_id_int = int(brand_id)

    models_data = []
    for model in models:
        models_data.append({
            'id': model.id,
            'name': model.name
        })

    response_data = {
        'success': True,
        'brand_id': brand_id_int,
        'models_count': len(models_data),
        'models': models_data
    }

    return JsonResponse(response_data)
