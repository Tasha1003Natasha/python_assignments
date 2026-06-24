from .connect import *
from .models import Quote

all_tags = set()

for q in Quote.objects():
    all_tags.update(q.tags)

print("All tags:")
print(sorted(all_tags))
