from django.shortcuts import render
# from .models import Input
# Create your views here.


def home(request):
    context = {}
    return render(request, 'home.html', context)

# def input(request):
#     items = Input.objects.all()
#     return render(request, 'input.html', {'input': items})