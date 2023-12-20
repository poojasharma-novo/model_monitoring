import smtplib
import ssl
from email.message import EmailMessage
import os

email_sender = 'pooja.sharma@novo.co'
email_password = 'gytv syfy jqxw zjyl'
#email_password = os.environ.get('EMAIL_PASSWORD')
email_receiver = 'psharma0880@gmail.com'
subject = 'RS2 Model Monitoring Report'
body = """
Model performance and data drift report. 
"""

# Path to the HTML document report
report_path = "/Users/pooja/Desktop/Pooja/model monitoring/GitHub/model_monitoring/reports/combined_reports/report_jan.html"

# Create the email message
msg = EmailMessage()
msg['From'] = email_sender
msg['To'] = email_receiver
msg['Subject'] = subject
msg.set_content(body)

# Attach the HTML report
with open(report_path, 'rb') as f:
   attachment = f.read()
msg.add_attachment(attachment, maintype='text', subtype='html', filename='report_jan.html')

# Send the email
context = ssl.create_default_context()
with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
   smtp.login(email_sender, email_password)
   smtp.send_message(msg)  
