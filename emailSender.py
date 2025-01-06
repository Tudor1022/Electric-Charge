import smtplib
from email.mime.text import MIMEText


def send_email(to_email, new_password):
    # Email content
    subject = "Your New Password"
    body = f"Your new password is: {new_password}"

    # Set up the email message
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'devgroupware34@gmail.com'
    msg['To'] = to_email

    # Send the email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('devgroupware34@gmail.com', 'qjgt dgka gpte xjwv')
        server.sendmail('devgroupware34@gmail.com', to_email, msg.as_string())
