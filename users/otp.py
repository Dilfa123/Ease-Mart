import smtplib

def send_otp_via_email(receiver_email, otp):
    sender_email = "dilfakottayil@gmail.com"
    sender_password = "nqktuosxexseyhed"  # Use Gmail App Password

    subject = "Your OTP Code"
    message = f"Subject: {subject}\n\nYour OTP is: {otp}\n"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, receiver_email, message)
    server.quit()
