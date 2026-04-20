from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('portal:dashboard')
    return redirect('portal:login')


@login_required
def dashboard(request):
    return render(request, 'portal/dashboard.html')
