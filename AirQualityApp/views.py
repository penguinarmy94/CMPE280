from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from . import models
import requests, json
import pymysql
import json
from django.http import HttpResponse

def index(request):
    """
    result = requests.get("https://api.openaq.org/v1/cities?limit=1", timeout=8)
    cities = result.json()['results']
    """
    return render(request, 'app.html', {'cities': "cities", 'lat': -30, 'lng': -17.5})

def latest(request):
    if request.method == "GET":
        if request.GET["search"]:
            zipcode = request.GET["search"]
            data = {"type": request.GET["search"]}
            packet = requests.get("http://www.airnowapi.org/aq/observation/zipCode/current/?format=application/json&zipCode=" + zipcode + "&distance=25&API_KEY=1BC71708-1C68-48AF-8742-7AEABACBE7F2", timeout=15)
            return HttpResponse(packet)
        else:
            return HttpResponse(json.dumps({"type": "none"}))
    else:
        return HttpResponse(json.dumps({"type": "not a request"}))

def future(request):
    return HttpResponse("404")

def updatePast(request):
    return HttpResponse("404")

def GetPastData(request):
    conn= pymysql.connect(host='airnow.cq2wcl14nou2.us-west-1.rds.amazonaws.com'
    ,user='root',password='password',db='airsafe')
    cur=conn.cursor()
    sql = "SELECT JSON_OBJECT('pm',pm,'ozone',ozone) FROM airsafe.AQ;"
    cur.execute(sql)
    data = cur.fetchall()
    return HttpResponse(json.dumps(data))
