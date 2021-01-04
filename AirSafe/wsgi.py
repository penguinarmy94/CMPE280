"""
WSGI config for AirSafe project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os, threading, datetime, time

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AirSafe.settings")

application = get_wsgi_application()

from AirQualityApp import views

def update():
    next_date = datetime.date.today() + datetime.timedelta(days=1)

    while True:
        day = datetime.date.today()

        if day == next_date:
            views.dayUpdate()
            next_date = day + datetime.timedelta(days=1)
        else:
            print("The day represented as today is: " + day.isoformat())
        
        time.sleep(60)
        
        # else:
        #     print("The current date and time is: " + day.isoformat() + " " + str(time))
    
update_thread = threading.Thread(target=update)

update_thread.start()