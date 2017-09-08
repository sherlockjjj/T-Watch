"""
This is a demo of sending daily email to users
"""
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# AWS Config
EMAIL_HOST = 'email-smtp.us-west-2.amazonaws.com'
EMAIL_HOST_USER = os.environ['email_host_user']
EMAIL_HOST_PASSWORD = os.environ['email_host_password']
EMAIL_PORT = 587

msg = MIMEMultipart('alternative')
msg['Subject'] = "Your Daily Twitter Master Report"
msg['From'] = os.environ['MY_EMAIL']
msg['To'] = os.environ['MY_EMAIL']

mime_text = MIMEText(html, 'html')
msg.attach(mime_text)

s = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
s.starttls()
s.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
s.sendmail(me, you, msg.as_string())
s.quit()
