from django.shortcuts import render

def home(request):
    return render(request, 'ai_app/main/home.html')

def landing_page(request):
    return render(request, 'ai_app/main/landingpage.html')

def contact_view(request):
    return render(request, 'ai_app/contact.html')
