# app/views.py
from django.shortcuts import render, redirect
from .forms import UserProfileForm


def user_profile_create(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success_page')  # Replace 'success_page' with your success page URL
    else:
        form = UserProfileForm()

    return render(request, 'user_profile_form.html', {'form': form})
