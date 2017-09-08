#sms testing
import os
from twilio.rest import Client

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']

client = Client(account_sid, auth_token)
body = "Yo Yo. Check it out! Twitter Master Alert! You might be interested in this tweet \n"
tweets = "Some Text"
body += tweets
client.messages.create(to=os.environ['MY_NUM'], from_=os.environ['TWILIO_NUM'], body=body)
