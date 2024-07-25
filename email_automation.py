import pandas as pd
import email
import schedule
import time
import imaplib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import dotenv
import logging

dotenv.load_dotenv()

sender_mail = os.getenv("SENDER_MAIL_ID")
sender_password = os.getenv("SENDER_PASSWORD")

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("email_automation.log"),
                              logging.StreamHandler()]
                    )


def send_mail(recipient, subject, body):
    msg = MIMEMultipart()
    msg['From'] = sender_mail
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_mail, sender_password)
        server.sendmail(
            sender_mail, recipient, msg.as_string()
        )
        server.quit()
        logging.info(f"Email sent to {recipient} with the subject: {subject}")
    except Exception as e:
        logging.error(f"Failed to send email to {recipient}: {e}")


def read_emails():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    try:
        mail.login(sender_mail, sender_password)
        mail.select("inbox")
        result, data = mail.search(None, "ALL")
        email_ids = data[0].split()

        for email_id in email_ids:
            result, message_data = mail.fetch(email_id, "(RFC822)")
            raw_email = message_data[0][1]
            msg = email.message_from_bytes(raw_email)
            logging.info(f"From: {msg['From']}, Subject: {msg['Subject']}")
            print("From:", msg["From"])
            print("Subject:", msg["Subject"])
            print("Body:", msg.get_payload(decode=True).decode())
            print("\n")
            logging.debug(f"Body: {msg.get_payload(decode=True).decode()}")

        mail.logout()
    except Exception as e:
        logging.error(f"Failed to read emails. Error: {e}")


def job():
    try:
        data = pd.read_csv('recipients.csv')
        for index, row in data.iterrows():
            recipient = row['Email']
            name = row['Name']
            subject = f"Hello, {name}!"
            body = f"Dear {name},\n\nThis is an automated email."
            send_mail(recipient, subject, body)
    except Exception as e:
        logging.error(f"Failed to process the job. Error: {e}")


schedule.every().day.at("09:00").do(job)

if __name__ == "__main__":
    logging.info("Starting the email automation system.")
    while True:
        schedule.run_pending()
        time.sleep(1)
