import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def send_email_alert(job_title, location, job_id):
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    smtp_server_name = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', 587))

    raw_receivers = os.getenv('RECEIVER_EMAILS', '')
    receiver_list = [email.strip() for email in raw_receivers.split(',') if email.strip()]
    if not receiver_list:
        print("No receiver emails found in .env")
        return
    
    # Create the email content
    job_url = f"https://hiring.amazon.com/app#/jobDetail?jobId={job_id}"

    try:
        # Open connection once for the whole batch
        with smtplib.SMTP(smtp_server_name, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            
            for receiver_email in receiver_list:
                message = MIMEMultipart()
                message["From"] = sender_email
                message["To"] = receiver_email
                message["Subject"] = f"🚨 New Amazon Job: {job_title} in {location}"

                body = f"""Role: {job_title}
Location: {location}
Job ID: {job_id}

Link to Apply: {job_url}"""
                message.attach(MIMEText(body, "plain"))
                
                server.send_message(message)
                print(f"Email sent successfully to {receiver_email} for job {job_id}")
    except Exception as e:
        print(f"Failed to send email batch: {e}")
