from django.shortcuts import render
from django.http import HttpResponse
from .models import Event
import pickle

def index(request):
    all_events = Event.objects.all()
    context = {'all_events': all_events}
    return render(request, 'bet_app/index.html', context)

