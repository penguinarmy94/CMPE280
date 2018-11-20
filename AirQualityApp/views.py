from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from . import models
import requests, json, pymysql, datetime
from . import forecast

current_url = ("http://www.airnowapi.org/aq/observation/zipCode/current/?format=application/json&zipCode=", "&distance=25&API_KEY=1BC71708-1C68-48AF-8742-7AEABACBE7F2")
past_url = ("http://www.airnowapi.org/aq/observation/zipCode/historical/?format=application/json&zipCode=", "&date=", "T00-0000&distance=25&API_KEY=1BC71708-1C68-48AF-8742-7AEABACBE7F2")

def index(request):

    try:
        zips = models.Zip.objects.all()
        points = []

        for zip in zips:
            aq = list(models.AQ.objects.filter(zipcode=zip.code).order_by('stamp').values())
            data = aq[len(aq) - 1]
            data["stamp"] = data["stamp"].isoformat()
            points.append(data)
        
        return render(request, 'app.html', { "import": json.dumps(points)})
    except Exception as e:
        print(str(e))
        return HttpResponse("Could not get the page requested")

def latest(request):
    if request.method == "GET":
        if request.GET["zip"]:
            zipcode = request.GET["zip"]
            code = models.Zip.objects.filter(code=zipcode)
            if code:
                data = list(models.AQ.objects.filter(zipcode=zipcode).values())
                data[0]["stamp"] = data[0]["stamp"].isoformat()
                return HttpResponse(json.dumps(data[0]))
            else:
                data = getNewData(zipcode)
                data[0]["stamp"] = data[0]["stamp"].isoformat()
                return HttpResponse(json.dumps(data[0]))
        else:
            return HttpResponse(json.dumps({"type": "none"}))
    else:
        return HttpResponse(json.dumps({"type": "not a request"}))

def future(request):
    #zips = models.Zip.objects.all()

    #historyUpdate(zips, datetime.date.today(), 20)

    #return HttpResponse("success")

    
    if request.method == "GET":
        if request.GET["zip"]:
            zipcode = request.GET["zip"]
            while True:
                code = models.Zip.objects.filter(code=zipcode)
                if code:
                    data = list(models.AQ.objects.filter(zipcode=zipcode).values('ozone'))
                    results = forecast.predict(zipcode, data)
                    print(results)
                    return HttpResponse(json.dumps(results))
        else:
            return HttpResponse(json.dumps({"type": "none"}))
    else:
        return HttpResponse(json.dumps({"type": "not a request"}))
    

def updatePast(request):
    zips = models.Zip.objects.all()

    weekUpdate(zips, datetime.date.today())

       
    return HttpResponse("success")

def GetPastData(request):
    if request.method == "GET":
        if request.GET["zip"]:
            zipcode = request.GET["zip"]

            sql = models.AQ.objects.filter(zipcode=zipcode).order_by("stamp")

            if sql:
                data = []
                for point in sql:
                    data.append({"pm": point.pm, "ozone": point.ozone, "stamp":point.stamp.isoformat()})
                
                return HttpResponse(json.dumps(data))
            else:
                return HttpResponse(json.dumps({"type": "none"}))

def weekUpdate(zips, today):

    for zip in zips:
        for day in range(7):
            date = today - datetime.timedelta(days=day)

            if date == today:
                try:
                    aq = requests.get(current_url[0] + zip.code + current_url[1], timeout = 10)    
                except:
                    print("Error unloading")
                    continue
            else:
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

def historyUpdate(zips, start, amount):
    today = datetime.date.today()

    for zip in zips:
        for day in range(amount):
            date = start - datetime.timedelta(days=day)

            if date == today:
                try:
                    aq = requests.get(current_url[0] + zip.code + current_url[1], timeout = 10)    
                except Exception as e:
                    print("Error unloading")
                    print(e)
                    continue
            else:
                try:
                    aq = requests.get(past_url[0] + zip.code + past_url[1] + date.isoformat() + past_url[2], timeout = 10)    
                except Exception as e:
                    print("Error unloading")
                    print(e)
                    continue
            
            aq = json.loads(aq.text)
            
            
            if aq:
                aq_object = models.History()
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
                print("Did not work")
                print(aq)
                continue

def dayUpdate():
    zips = models.Zip.objects.all()

    for zip in zips:
        aq = models.AQ.objects.filter(zipcode=zip.code).order_by("stamp")[0]
        history = models.History()
        print(aq.stamp)

        try:
            new_aq = json.loads(requests.get(current_url[0] + zip.code + current_url[1]).text)
            if new_aq:
                date = new_aq[0]["DateObserved"].split("-")
                aq.stamp = datetime.date(year=int(date[0]), month=int(date[1]), day=int(date[2]))
                history.stamp = datetime.date(year=int(date[0]), month=int(date[1]), day=int(date[2]))
                history.city = new_aq[0]["ReportingArea"]
                history.country = "US"
                history.latitude = new_aq[0]["Latitude"]
                history.longitude = new_aq[0]["Longitude"]
                history.state = new_aq[0]["StateCode"]

                for theData in new_aq:
                    if theData["ParameterName"] == "PM2.5":
                        aq.pm = theData["AQI"]
                        history.pm = theData["AQI"]
                    elif theData["ParameterName"] == "O3" or theData["ParameterName"] == "OZONE":
                        aq.ozone = theData["AQI"]
                        history.ozone = theData["AQI"]
                    else:
                        continue
                
                forecast.retrain(aq.pm, aq.ozone, datetime.date.today().isoformat(), aq.zipcode)
                aq.save()
                history.save()
        except Exception as e:
            print(str(e))
            return

def getNewData(zipcode):

    try:
        data = json.loads(requests.get(current_url[0] + zipcode + current_url[1], timeout=10).text)
        if data:
            data = models.Zip(code=zipcode)
            data.save()
            weekUpdate([data], datetime.date.today())
            historyUpdate([data], datetime.date.today(), 20)

            historyData = models.History.objects.filter(zipcode=zicpde)

            for obj in historyData:
                forecast.retrain(obj.pm, obj.ozone, obj.stamp.isoformat(), obj.zipcode)

            data = list(models.AQ.objects.filter(zipcode=zipcode).values())

            return data
        else:
            return {"type": "missing data"}
    except Exception as e:
        print(str(e))
        try:
            code = models.Zip.objects.filter(code=zipcode).get()
            code.delete()
            code = models.AQ.objects.filter(code=zipcode).delete()
            code.delete()
            return [{"type": "connection error"}]
        except:
            return [{"type": "connection error"}]           
                
            


