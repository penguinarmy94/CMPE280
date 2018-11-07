from django.shortcuts import render
import pymysql
import json
from django.http import HttpResponse
#import requests, socket
#from geoip import geolite2

# Create your views here.
def index(request):
    """
    result = requests.get("https://api.openaq.org/v1/cities?limit=1", timeout=8)
    cities = result.json()['results']
    """
    return render(request, 'app.html', {'cities': "cities", 'lat': 0, 'lng': 0})

def latest(request):
    """
    location = geolite2.lookup(socket.gethostbyname(socket.gethostname()))# geocoder.ipinfo('me').latlng
    print(location)
    result = requests.get("https://api.openaq.org/v1/latest?coordinates=" + str(-30) + "," + str(-17.5) + "&radius=50", timeout=8)
    print(result.json())
    info = result.json()['results']
    """

    return render(request, 'index.html', {'cities': "", 'lat': -30, 'lng': -17.5})
    #result = requests.get("https://api.openaq.org/v1/latest")

def GetPastData(request):
    conn= pymysql.connect(host='airnow.cq2wcl14nou2.us-west-1.rds.amazonaws.com'
    ,user='root',password='password',db='airsafe')
    cur=conn.cursor()
    sql = "SELECT JSON_OBJECT('pm',pm,'ozone',ozone) FROM airsafe.AQ;"
    cur.execute(sql)
    data = cur.fetchall()
    return HttpResponse(json.dumps(data))