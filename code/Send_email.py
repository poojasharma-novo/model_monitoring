import smtplib
import ssl
from email.message import EmailMessage
import os

def send_email(email_sender, email_password, email_receiver, month):
    try: 
        subject = 'RS2 Model Monitoring Report'
        body = f"""
        Model performance and data drift report for {month}
        """

        # Path to the HTML document report
        report_path = "/Users/pooja/Desktop/Pooja/model monitoring/GitHub/model_monitoring/reports/combined_reports/report_" + month + ".html"
 
        # Create the email message
        msg = EmailMessage()
        msg['From'] = email_sender
        msg['To'] = email_receiver
        msg['Subject'] = subject
        msg.set_content(body)

        # Attach the HTML report
        with open(report_path, 'rb') as f:
            attachment = f.read()
        msg.add_attachment(attachment, maintype='text', subtype='html', filename='report_' + month + '.html')

        # Send the email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.send_message(msg)  

    except smtplib.SMTPAuthenticationError as e:
        print('Authentication error:', e)
    except smtplib.SMTPException as e:
        print('Error sending email:', e)
    except OSError as e:
        print('Error opening attachment:', e)
    except Exception as e:
        print('Unexpected error:', e)

# if __name__ == "__main__": 

#     email_sender = 'pooja.sharma@novo.co'
#     email_password = os.environ.get('EMAIL_PASSWORD')
#     email_receiver = 'psharma0880@gmail.com'
    
#     send_email(email_sender, email_password, email_receiver)
 

