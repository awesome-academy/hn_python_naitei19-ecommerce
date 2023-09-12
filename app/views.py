from django.shortcuts import render

def item_list(request):
    context = {
        
    }
    return render(request, "home.html", context)
