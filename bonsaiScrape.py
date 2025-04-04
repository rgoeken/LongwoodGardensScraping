import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
# import schedule  # Commented out for testing
# import time      # Commented out for testing

def send_email(subject, body):
    smtp_server = "smtp.gmail.com"
    port = 587  # For STARTTLS

    # Fetch credentials from environment variables
    sender_email = "rachel.goeken@gmail.com"
    receiver_email = "rachel.goeken@gmail.com"
    password = ""         # Your 16-digit app password

    if not sender_email or not receiver_email or not password:
        print("Missing email credentials in environment variables.")
        return

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()  # Secure the connection
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print("Error sending email:", e)
    finally:
        server.quit()

def check_new_bonsai_class():
    url = "https://longwoodgardens.org/events-performances/classes-lectures"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        print("Error fetching events page:", e)
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all event containers (each event has class "node--type-event")
    event_containers = soup.select("div.node--type-event")
    
    # List to hold tuples of (event_title, event_link)
    events_list = []

    for event in event_containers:
        # Extract the event title from the element with class "o-card__text-title"
        title_element = event.select_one('.o-card__text-title')
        title = title_element.get_text(strip=True) if title_element else ""
        
        # Process events that contain either "bonsai" or "mushroom" in the title.
        # Skip the event if it doesn't have either keyword.
        if "bonsai" not in title.lower() and "mushroom" not in title.lower():
            continue

        # Check the event summary for availability indicators
        summary_element = event.select_one('.f-text--summary')
        summary_text = summary_element.get_text(strip=True) if summary_element else ""
        if ("sold out" in summary_text.lower() or 
            "waitlist" in summary_text.lower() or 
            "registration closed" in summary_text.lower()):
            print(f"Bonsai class '{title}' found but it is not available (sold out, waitlist, or registration closed).")
            continue

        # Use an escaped CSS selector for the details container
        details_container = event.select_one('div.max-w-\\[65ch\\]')
        if not details_container:
            print("Bonsai class found but no details container available.")
            continue
        
        link_element = details_container.find('a', href=True)
        if not link_element:
            print("Bonsai class found but registration link is missing.")
            continue

        event_link = link_element['href']
        if not event_link.startswith("http"):
            event_link = "https://longwoodgardens.org" + event_link

        events_list.append((title, event_link))

    if events_list:
        # Build a body text listing all the events
        body_lines = ["The following new bonsai classes are available:\n"]
        for title, link in events_list:
            body_lines.append(f"{title}\nRegister here: {link}\n")
        body = "\n".join(body_lines)
        subject = "New Bonsai Classes Available!"
        send_email(subject, body)
    else:
        print("No new bonsai classes with available spots found.")

def job():
    print("Checking for new bonsai classes...")
    check_new_bonsai_class()

if __name__ == "__main__":
    print("Starting the Longwood Gardens bonsai class monitor...")
    # For testing, run the job once.
    job()

    # Uncomment the lines below to enable hourly scheduling after testing:
    # import schedule
    # import time
    # schedule.every().hour.do(job)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)