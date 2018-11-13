import smtplib
from . import models

#send email
def send_email():
	users = models.User.objects.all();
	for user in users:
		aq = models.AQ.objects.filter(zipcode=user.zipcode).order_by("-stamp")[0]
		sender = "cmpe280.airsafe@gmail.com"
		receiver = user.email
		message = """From: AirSafe <cmpe280.airsafe@gmail.com>
To: """ + user.email + """
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
			server.login("cmpe280.airsafe@gmail.com", "airsafe280")
			server.sendmail(sender, receiver, message)
			server.close()
			print ("Email sent successfully")
		except smtplib.SMTPException:
			print ("Error: Unable to send the email")