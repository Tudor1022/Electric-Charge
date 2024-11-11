import smtplib
from email.mime.text import MIMEText


def send_email(to_email, new_password):
    # Email content
    subject = "Your New Password"
    body = f"Your new password is: {new_password}"

    # Set up the email message
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'your_email@example.com'
    msg['To'] = to_email

    # Send the email
    with smtplib.SMTP('smtp.example.com', 587) as server:
        server.starttls()
        server.login('your_email@example.com', 'your_email_password')
        server.sendmail('your_email@example.com', to_email, msg.as_string())
