from django.shortcuts import get_object_or_404, render

from .models import Quote, Author, Tag


def main(request):
    quotes = Quote.objects.select_related("author").prefetch_related("tags")
    return render(request, 'quotes/index.html', context={"quotes": quotes})


def author_detail(request, author_id):
    author = Author.objects.get(id=author_id)
    return render(request, "quotes/author_detail.html", {"author": author})


def tag_detail(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)

    quotes = Quote.objects.filter(tags=tag).select_related(
        "author").prefetch_related("tags")

    return render(
        request,
        "quotes/tag_detail.html",
        {
            "tag": tag,
            "quotes": quotes,
        }
    )
