from django.shortcuts import render
from .models import Person
import json


def home(request):
    query = request.GET.get('q', '')
    if query:
        persons = Person.objects.filter(name__icontains=query)
    else:
        persons = Person.objects.all()

    persons_json = json.dumps(
        [{'name': person.name, 'age': person.age} for person in persons])

    return render(request, 'home.html', {'persons_json': persons_json, 'query': query})
    # return render(request, 'home.html', {'people': people, 'query': query})