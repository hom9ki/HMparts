from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Garage, UserCar
from django.contrib import messages
from .forms import AddCarForm


@login_required
def garage_list(request):
    if request.user.is_authenticated:
        auto_list = Garage.objects.filter(user=request.user)
        return render(request, 'garage.html', {'garage': auto_list})
    else:
        return redirect('login')


@login_required
def add_car(request):
    pass


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
