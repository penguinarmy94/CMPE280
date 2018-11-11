import smtplib

#send email
def send_email():
	sender = "garyhsiao1219@gmail.com"
	receiver = "garyhsiao1219@gmail.com"
	message = """From: AirSafe <airsafe@gmail.com>
To: Yi-Chin Hsiao <garyhsiao1219@gmail.com>
Subject: AirSafe Test Email

This is a test email from AirSafe.
"""

	try:
		server = smtplib.SMTP("smtp.gmail.com", 587)
		server.ehlo()
		server.starttls()
		server.ehlo()
		server.login("garyhsiao1219@gmail.com", "yichin0091")
		server.sendmail(sender, receiver, message)
		server.close()
		print ("Email sent successfully")
	except smtplib.SMTPException:
		print ("Error: Unable to send the email")
		
# import pymysql
# 
# conn = pymysql.connect(host='airnow.cq2wcl14nou2.us-west-1.rds.amazonaws.com', 
# 					   user='root',password='password',db='airsafe')
# cur = conn.cursor()
# sql = "SELECT email, zipcode FROM airsafe.User;"
# cur.execute(sql)
# users = cur.fetchall()
# for user in users:
# 	print("{0} {1}".format(user[0], user[1]))