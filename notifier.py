import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def send_email_alert(job_title, location, job_id):
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    receiver_email = os.getenv('RECEIVER_EMAIL')
    
    # Create the email content
    job_url = f"https://hiring.amazon.com/app#/jobDetail?jobId={job_id}"
    
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = f"🚨 New Amazon Job: {job_title} in {location}"

    body = f"""
    A new job has been posted that matches your criteria!
    
    Role: {job_title}
    Location: {location}
    Job ID: {job_id}
    
    Link to Apply: {job_url}
    """
    message.attach(MIMEText(body, "plain"))

    try:
        # Connect to the server and send email
        with smtplib.SMTP(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT'))) as server:
            server.starttls() # Secure the connection
            server.login(sender_email, sender_password)
            server.send_message(message)
            server.quit()
        print(f"Email sent successfully for job {job_id}")
    except Exception as e:
        print(f"Failed to send email: {e}")
