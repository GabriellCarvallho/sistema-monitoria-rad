from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import login

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(request, user)

            messages.success(
                request,
                f'Conta criada para {user.username}!'
            )
            return redirect('artigos:lista')

    else:
        form = UserCreationForm()
        return render(request, 'registration/register.html', {'form': form})