from django.shortcuts import render
import requests, socket
from geoip import geolite2

# Create your views here.
def index(request):
    result = requests.get("https://api.openaq.org/v1/cities?limit=1", timeout=8)
    cities = result.json()['results']
    return render(request, 'index.html', {'cities': cities, 'lat': 0, 'lng': 0})

def latest(request):
    location = geolite2.lookup(socket.gethostbyname(socket.gethostname()))# geocoder.ipinfo('me').latlng
    print(location)
    result = requests.get("https://api.openaq.org/v1/latest?coordinates=" + str(location[0]) + "," + str(location[1]) + "&radius=50", timeout=8)
    print(result.json())
    info = result.json()['results']

    return render(request, 'index.html', {'cities': info, 'lat': location[0], 'lng': location[1]})
    #result = requests.get("https://api.openaq.org/v1/latest")
