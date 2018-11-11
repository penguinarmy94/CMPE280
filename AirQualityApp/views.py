from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from . import models
import requests, json, pymysql, datetime

current_url = ("http://www.airnowapi.org/aq/observation/zipCode/current/?format=application/json&zipCode=", "&distance=25&API_KEY=1BC71708-1C68-48AF-8742-7AEABACBE7F2")
past_url = ("http://www.airnowapi.org/aq/observation/zipCode/historical/?format=application/json&zipCode=", "&date=", "T00-0000&distance=25&API_KEY=1BC71708-1C68-48AF-8742-7AEABACBE7F2")

def index(request):
    return render(request, 'app.html', {'cities': "cities", 'lat': -30, 'lng': -17.5})

def latest(request):
    if request.method == "GET":
        if request.GET["zip"]:
            zipcode = request.GET["zip"]
            code = models.Zip.objects.filter(code=zipcode)
            if code:
                data = list(models.AQ.objects.filter(zipcode=zipcode).order_by('stamp').values())
                data[0]["stamp"] = data[0]["stamp"].isoformat()
                return HttpResponse(json.dumps(data[0]))
            else:
                data = getCurrent(zipcode)
                return HttpResponse(json.dumps(data))
        else:
            return HttpResponse(json.dumps({"type": "none"}))
    else:
        return HttpResponse(json.dumps({"type": "not a request"}))

def future(request):
    return HttpResponse("404")

def updatePast(request):
    zips = models.Zip.objects.all()
    time = datetime.datetime.today().hour

    if time >= 16:
        weekUpdate(zips, datetime.date.today() + datetime.timedelta(days=1))
    else:
        weekUpdate(zips, datetime.date.today())
        
    return HttpResponse("success")

def GetPastData(request):
    """
    conn= pymysql.connect(host='airnow.cq2wcl14nou2.us-west-1.rds.amazonaws.com'
    ,user='root',password='password',db='airsafe')
    cur=conn.cursor()
    sql = "SELECT JSON_OBJECT('pm',pm,'ozone',ozone) FROM airsafe.AQ;"
    cur.execute(sql)
    data = cur.fetchall()
    """
    sql = models.AQ.objects.filter(zipcode="95112").order_by("stamp")
    data = []

    for point in sql:
        data.append({"pm": point.pm, "ozone": point.ozone})

    return HttpResponse(json.dumps(data))

def weekUpdate(zips, today):

    for zip in zips:
        for day in range(8):
            date = today - datetime.timedelta(days=day)
            try:
                aq = requests.get(past_url[0] + zip.code + past_url[1] + date.isoformat() + past_url[2], timeout = 10)    
            except:
                print("Error unloading")
                continue
            
            aq = json.loads(aq.text)
            
            
            if aq:
                aq_object = models.AQ()
                aq_object.zipcode = zip.code
                aq_object.city = aq[0]["ReportingArea"]
                aq_object.country = "US"
                aq_object.state = aq[0]["StateCode"]
                aq_object.latitude = aq[0]["Latitude"]
                aq_object.longitude = aq[0]["Longitude"]
                aDate = aq[0]["DateObserved"].split("-")
                aq_object.stamp = datetime.date(year=int(aDate[0]), month=int(aDate[1]), day=int(aDate[2]))
                for data in aq:
                    if data["ParameterName"] == "PM2.5":
                        aq_object.pm = data["AQI"]
                    elif data["ParameterName"] == "O3" or data["ParameterName"] == "OZONE":
                        aq_object.ozone = data["AQI"]
                    else:
                        continue
                if not aq_object.ozone:
                    aq_object.ozone = 0
                if not aq_object.pm:
                    aq_object.pm = 0

                aq_object.save()
            else:
                continue
                
def getCurrent(zipcode):
    try:
        data = json.loads(requests.get(current_url[0] + zipcode + current_url[1], timeout=10).text)
        if data:
            data = models.Zip(code=zipcode)
            data.save()
            if datetime.datetime.today().hour < 16:
                weekUpdate([data], datetime.date.today())
            else:
                weekUpdate([data], datetime.date.today() + datetime.timedelta(days=1))
            
            packet = json.loads(requests.get(current_url[0] + zipcode + current_url[1], timeout=10).text)
            data = {}
            data["id"] = 0
            data["zipcode"] = zipcode
            data["city"] = packet[0]["ReportingArea"]
            data["country"] = "US"
            data["state"] = packet[0]["StateCode"]
            data["latitude"] = packet[0]["Latitude"]
            data["longitude"] = packet[0]["Longitude"]
            data["stamp"] = packet[0]["DateObserved"]
            #data["stamp"] = datetime.date(year=int(aDate[0]), month=int(aDate[1]), day=int(aDate[2]))
            for theData in packet:
                if theData["ParameterName"] == "PM2.5":
                    data["pm"] = theData["AQI"]
                elif theData["ParameterName"] == "O3" or theData["ParameterName"] == "Ozone":
                    data["ozone"] = theData["AQI"]
                else:
                    continue
            if not data["pm"]:
                data["pm"] = 0
            if not data["ozone"]:
                data["ozone"] = 0

            return data

        else:
            return {"type": "missing data"}
    except Exception as e:
        print(str(e))
        try:
            code = models.Zip.objects.filter(code=zipcode).get()
            code.delete()
            return [{"type": "connection error"}]
        except:
            return [{"type": "connection error"}]           
                
            


