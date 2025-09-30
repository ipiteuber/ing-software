from django.shortcuts import render

# ---------------------- Index ----------------------
def landing_page(request):
    return render(request, 'landing_page.html')