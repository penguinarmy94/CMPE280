from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from . import models

import requests, json, datetime, smtplib, random, os
from . import forecast

current_url = ("http://www.airnowapi.org/aq/observation/zipCode/current/?format=application/json&zipCode=", "&distance=25&API_KEY=1BC71708-1C68-48AF-8742-7AEABACBE7F2")
past_url = ("http://www.airnowapi.org/aq/observation/zipCode/historical/?format=application/json&zipCode=", "&date=", "T00-0000&distance=25&API_KEY=1BC71708-1C68-48AF-8742-7AEABACBE7F2")

def index(request):

    print(datetime.datetime.today().hour)

    try:
        zips = models.Zip.objects.all()
        points = []

        for zip in zips:
            aq = list(models.AQ.objects.filter(zipcode=zip.code).order_by('stamp').values())
            data = aq[len(aq) - 1]
            data["stamp"] = data["stamp"].isoformat()
            points.append(data)

        json_data = {}


        with open("LocalizationData.json", encoding="utf-8") as config:
            json_data = json.load(config)

        if "local" in request.GET:
            json_data = json_data[request.GET["local"]]
            json_data["region"] = request.GET["local"]
        else:
            json_data = json_data["EN"]
            json_data["region"] = "EN"

        json_data["import"] = json.dumps(points)
        json_data["GOOGLE_MAPS_API_KEY"] = get_credentials(".credentials/google-maps-api.json")["key"]

        return render(request, 'app.html', json_data)
    except Exception as e:
        print(str(e))
        return HttpResponse("Could not get the page requested")

def get_credentials(credentials_path):
    default = { "key" : "" }

    if os.path.exists(credentials_path) and credentials_path.endswith(".json"):
        try:
            with open(credentials_path, "r") as json_reader:
                return json.load(json_reader)
        except Exception:
            print(f"Could not credentials for the path {credentials_path}")
    
    return default
        
def latest(request):
    if request.method == "GET" and request.is_ajax():
        zipcode = getZipcode(request)

        if not zipcode:
            return HttpResponse(json.dumps({"type": "none"}))

        code = models.Zip.objects.filter(code=zipcode)

        if code:
            data = list(models.AQ.objects.filter(zipcode=zipcode).values())
            data[0]["stamp"] = data[0]["stamp"].isoformat()
            return HttpResponse(json.dumps(data[0]))
        else:
            data = getNewData(zipcode)
            print(data[0])
            try:
                data[0]["stamp"] = data[0]["stamp"].isoformat()
            except:
                return HttpResponse(json.dumps(data))

            return HttpResponse(json.dumps(data[0]))
    else:
        return HttpResponse(json.dumps({"type": "not a request"}))
    
def future(request):
    if request.method == "GET" and request.is_ajax():
        zipcode = getZipcode(request)

        if not zipcode:
            return HttpResponse(json.dumps({"type": "none"}))

        code = models.Zip.objects.filter(code=zipcode)
        if code:
            forecasted_data = list(models.Forecast.objects.filter(zipcode=zipcode).order_by("stamp").values())

<<<<<<< HEAD
            if not forecasted_data or len(forecasted_data) == 0 or forecasted_data[0]["stamp"] <= datetime.datetime.now().date():
                print("New Forecasted Data")
=======
            if not forecasted_data or len(forecasted_data) == 0:
                print(forecasted_data)
>>>>>>> ec9f0420a73d53231e458823da0290110959bd03
                data = list(models.AQ.objects.filter(zipcode=zipcode).values('ozone'))
                results = forecast.predict(zipcode, data)
                addForecasts(zipcode, results)
                forecasted_data = list(models.Forecast.objects.filter(zipcode=zipcode).order_by("stamp").values())
<<<<<<< HEAD
                temp_forecasted_data = []
                tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).date()
                seven_days = tomorrow + datetime.timedelta(days=7)

                for data in forecasted_data:
                    if data["stamp"] >= tomorrow and data["stamp"] <= seven_days:
                        temp_forecasted_data.append(data)
                
                forecasted_data = temp_forecasted_data
=======
>>>>>>> ec9f0420a73d53231e458823da0290110959bd03
            else:
                print("There is forecasted data already set")

            for date in forecasted_data:
                date["stamp"] = date["stamp"].isoformat()

            return HttpResponse(json.dumps(forecasted_data))
        else:
            return HttpResponse(json.dumps({"type": "none"}))
    else:
        return redirect(index)

def updatePast(request):
    zips = list(models.Zip.objects.all())

    historyWeekUpdate(zips, datetime.date.today())

    return HttpResponse("success")

def updateFuture():
    zips = models.Zip.objects.all()

    forecastWeekUpdate(zips, datetime.date.today())

    return True

def GetPastData(request):
    if request.method == "GET" and request.is_ajax():
        zipcode = getZipcode(request)

        if not zipcode:
            return HttpResponse(json.dumps({"type": "none"}))

        sql = list(models.AQ.objects.filter(zipcode=zipcode).order_by("stamp"))

        if len(sql) > 0:
            if sql[0].stamp < datetime.date.today():
                historyWeekUpdate([zipcode], datetime.date.today())
                sql = list(models.AQ.objects.filter(zipcode=zipcode).order_by("stamp"))[-7:]
            
            data = []
            
            for point in sql:
                data.append({"pm": point.pm, "ozone": point.ozone, "stamp": point.stamp.isoformat()})
            
            return HttpResponse(json.dumps(data))
        else:
            return HttpResponse(json.dumps({"type": "none"}))

    else:
        return redirect(index)

def verifyEmailAndZipcode(request):
    zipcode = request.GET["zipcode"]
    code = models.Zip.objects.filter(code=zipcode)
    if not code.exists():
        new_code = json.loads(requests.get(current_url[0] + zipcode + current_url[1], timeout=10).text)
        if new_code:
            new_code = models.Zip(code=zipcode)
            new_code.save()
            historyWeekUpdate([new_code], datetime.date.today())
            historyUpdate([new_code], datetime.date.today(), 20)
            historyData = models.History.objects.filter(zipcode=zipcode)
            for obj in historyData:
                forecast.retrain(obj.pm, obj.ozone, obj.stamp.isoformat(), obj.zipcode)
        else:
            return HttpResponse("no data")
    number = range(0, 10)
    digits = random.sample(number, 6)
    code = "".join(map(str, digits))
    email = request.GET["email"]
    sender = "luad.developer@gmail.com"
    receiver = email
<<<<<<< HEAD
    message = """From: AirSafe <luad.developer@gmail.com>
=======
    message = """From: AirSafe <cmpe280.airsafe@gmail.com>
>>>>>>> ec9f0420a73d53231e458823da0290110959bd03
        To: """ + email + """
        Subject: Verification Code

        Thank you for subscribing AirSafe! Your verification code is """ + code + """.


        If you didn't subscribe our website, just ignore this email! Apology for our mistake!
    """

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender, "yO3%h!w*MKzn*sE637$U%")
        server.sendmail(sender, receiver, message)
        server.close()
        print ("Email sent successfully")
        return HttpResponse(code)
    except smtplib.SMTPException as error:
        print (f"Error: Unable to send the email because {error}")
        return HttpResponse("error")

def subscription(request):
    email = request.GET["email"]
    zipcode = request.GET["zipcode"]
    user = models.User.objects.filter(email=email)
    if user.exists():
        old_user = user[0]
        old_user.zipcode = zipcode
        old_user.save()
        print ("Existed user updated into the DB successfully!")
    else:
        new_user = models.User()
        new_user.email = email
        new_user.zipcode = zipcode
        new_user.save()
        print ("New user inserted into the DB successfully!")

    aq = models.AQ.objects.filter(zipcode=zipcode).order_by("-stamp")[0]
    sender = "luad.developer@gmail.com"
    receiver = email
<<<<<<< HEAD
    message = """From: AirSafe <luad.developer@gmail.com>
=======
    message = """From: AirSafe <cmpe280.airsafe@gmail.com>
>>>>>>> ec9f0420a73d53231e458823da0290110959bd03
        To: """ + email + """
        Subject: AirSafe Test Email

        City: """ + aq.city + """    State: """ + aq.state + """
        Date: """ + str(aq.stamp) + """
        Ozone(O3) AQI: """ + str(aq.ozone) + """
        PM2.5 AQI: """ + str(aq.pm)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login("luad.developer@gmail.com", "yO3%h!w*MKzn*sE637$U%")
        server.sendmail(sender, receiver, message)
        server.close()
        print ("Email sent successfully")
        return HttpResponse("done")
    except smtplib.SMTPException as error:
        print (f"Error: Unable to send the email because {error}")
        return HttpResponse("error")

<<<<<<< HEAD
def historyWeekUpdate(zips, today):
=======
def weekUpdate(zips, today):
>>>>>>> ec9f0420a73d53231e458823da0290110959bd03
    error = "Error Unloading"

    for zip in zips:
        for day in range(7):
            date = today - datetime.timedelta(days=day)
            entry = models.AQ.objects.filter(zipcode=zip).filter(stamp=date)

            if len(entry) > 0:
                continue

            if date == today:
                try:
                    aq = requests.get(current_url[0] + zip.code + current_url[1], timeout = 10)
                except Exception:
                    print(error)
                    continue
            else:
                try:
                    aq = requests.get(past_url[0] + zip.code + past_url[1] + date.isoformat() + past_url[2], timeout = 10)
                except Exception:
                    print(error)
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

def forecastWeekUpdate(zips, today):
    error = "Error Unloading"
    number_of_days = 7

    for zip in zips:
        forecasted_dates = list(models.Forecast.objects.filter(zipcode=zip).values("stamp"))
        previous_data = list(models.AQ.objects.filter(zipcode=zip).values('ozone').order_by("stamp"))
        new_data = []

        for day in range(number_of_days):
            new_date = today + datetime.timedelta(days=day+1)

            if not new_date in forecasted_dates:
                data_index = -1*(number_of_days) + day
                new_day_forecast = forecast.predict(zip.code, [previous_data[data_index]])

                if new_day_forecast:
                    new_data += new_day_forecast
        
        addForecasts(zip, new_data)

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
                if not aq_object.ozone and not aq_object.pm:
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
                history.zipcode = zip.code

                for theData in new_aq:
                    if theData["ParameterName"] == "PM2.5":
                        aq.pm = theData["AQI"] if theData["AQI"] else 0
                        history.pm = theData["AQI"] if theData["AQI"] else 0
                    elif theData["ParameterName"] == "O3" or theData["ParameterName"] == "OZONE":
                        aq.ozone = theData["AQI"] if theData["AQI"] else 0
                        history.ozone = theData["AQI"] if theData["AQI"] else 0
                    else:
                        continue

                #forecast.retrain(aq.pm, aq.ozone, datetime.date.today().isoformat(), aq.zipcode)
                models.Forecast.objects.filter(zipcode=zip.code).delete()
                results = forecast.predict(zip.code, list(models.AQ.objects.filter(zipcode=zip.code).values("ozone")))
                addForecasts(zip.code, results)
                aq.save()
                history.save()
        except Exception as e:
            print(str(e))
            continue

def getNewData(zipcode):

    try:
        data = json.loads(requests.get(current_url[0] + zipcode + current_url[1], timeout=10).text)
        if data:
            data = models.Zip(code=zipcode)
            data.save()
            historyWeekUpdate([data], datetime.date.today())
            historyUpdate([data], datetime.date.today(), 20)

            #for obj in historyData:
            #    forecast.retrain(obj.pm, obj.ozone, obj.stamp.isoformat(), obj.zipcode)

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

def addForecasts(zipcode, data):
    if len(data) <= 0:
        return
    else:
        for point in data:
            forecast = models.Forecast()
            forecast.pm = point["pm"]
            forecast.stamp = point["stamp"]
            forecast.zipcode = zipcode
            forecast.save()

def getZipcode(request):
    zipcode = ""

    if not request.GET["zip"] == "":
        zipcode = request.GET["zip"]
    else:
        return None

    return zipcode
