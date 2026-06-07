import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def send_test_email():
    """Send a test email to verify email configuration and notify recipients they're opted in."""
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    smtp_server_name = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', 587))

    raw_receivers = os.getenv('RECEIVER_EMAILS', '')
    receiver_list = [email.strip() for email in raw_receivers.split(',') if email.strip()]
    
    if not receiver_list:
        print("❌ No receiver emails found in .env file")
        return False
    
    print(f"📧 Sender: {sender_email}")
    print(f"📬 Recipients: {', '.join(receiver_list)}")
    print(f"🌐 SMTP Server: {smtp_server_name}:{smtp_port}")
    print()

    # Get job monitoring settings
    raw_job_titles = os.getenv("TARGET_JOB_TITLES", "Amazon Fulfillment Center Warehouse Associate")
    job_list = [title.strip() for title in raw_job_titles.split(",")]
    lat = os.getenv("TARGET_LAT", "36.1690921")
    lng = os.getenv("TARGET_LNG", "-115.1405767")
    distance = os.getenv("TARGET_DISTANCE_MILES", "50")
    interval = os.getenv("CHECK_INTERVAL_SECONDS", "300")

    try:
        # Open connection once for all recipients
        with smtplib.SMTP(smtp_server_name, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            
            for receiver_email in receiver_list:
                message = MIMEMultipart()
                message["From"] = sender_email
                message["To"] = receiver_email
                message["Subject"] = "✅ Amazon Job Monitor - You're Opted In!"

                # Create job titles list for email body
                job_titles_formatted = "\n".join([f"  • {title}" for title in job_list])

                body = f"""What's up!

This is a test message from the Amazon Warehouse Job Monitor.

📋 MONITORING SETTINGS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Job Titles Being Monitored:
{job_titles_formatted}

📍 Search Area:
  Location: Latitude {lat}, Longitude {lng}
  Radius: {distance} miles

⏱️ Check Interval:
  Every {int(interval) // 60} minutes ({interval} seconds)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

When new jobs matching these criteria are found, you will receive an email alert with:
  🚨 Job Title
  📍 Location
  🔗 Direct application link

Good luck lil bro! 🎯
"""
                message.attach(MIMEText(body, "plain"))
                
                server.send_message(message)
                print(f"✅ Test email sent successfully to {receiver_email}")
        
        print()
        print("🎉 All test emails sent successfully!")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ SMTP Authentication failed - check your SENDER_EMAIL and SENDER_PASSWORD")
        print("   For Gmail, make sure you're using an App Password, not your regular password")
        return False
    except Exception as e:
        print(f"❌ Failed to send test emails: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("  AMAZON JOB MONITOR - EMAIL TEST")
    print("=" * 60)
    print()
    
    success = send_test_email()
    
    if success:
        print()
        print("✅ Email system is working correctly!")
    else:
        print()
        print("❌ Please fix the issues above and try again.")
