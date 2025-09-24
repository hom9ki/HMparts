from django.contrib.auth import authenticate, logout, login, update_session_auth_hash
from django.shortcuts import render, redirect
from .forms import LoginForm, RegisterForm, ChangePasswordForm, EditProfileForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def user_login(request):
    if request.user.is_authenticated:
        return redirect('product:index')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'product:index')
                return redirect(next_url)
            else:
                messages.error(request, 'Неверное имя пользователя или пароль')

    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    return render(request, 'logout_confirm.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('product:index')

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        password2 = request.POST.get('password2')
        print(f"DEBUG: password2={password2}")
        print("POST data keys:", list(request.POST.keys()))
        print("Form fields:", list(form.fields.keys()))
        print("Form data:", request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password2'])
                user.save()
                login(request, user)
                return redirect('product:index')
            except Exception as e:
                messages.error(request, 'Ошибка регистрации')
        else:
            print(form.errors)

    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required
def  change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST, )
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('product:index')
        else:
            print(form.errors)
    else:
        form = ChangePasswordForm(request.user)
    return render(request, 'change_password.html', {'form': form})

@login_required
def profile(request):
    user = request.user
    return render(request, 'profile.html', {'user': user})

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            redirect('account:profile')
        else:
            print(form.errors)
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'profile_edit.html', {'form': form})
