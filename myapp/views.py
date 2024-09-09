from django.shortcuts import render
from .models import Sequence
import json


def home(request):
    query = request.GET.get('q', '')
    if query:
        sequences = Sequence.objects.filter(protein__icontains=query)
    else:
        sequences = Sequence.objects.all()

    sequence_json = json.dumps(
        [{'individual': seq.individual, 'protein': seq.protein} for seq in sequences])

    return render(request, 'home.html', {'sequence_json': sequence_json, 'query': query})