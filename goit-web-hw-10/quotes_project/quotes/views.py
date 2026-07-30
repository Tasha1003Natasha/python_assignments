from django.shortcuts import render

from .models import Quote

# Create your views here.


def main(request):
    quotes = Quote.objects.select_related("author").prefetch_related("tags")
    return render(request, 'quotes/index.html', context={"quotes": quotes})
