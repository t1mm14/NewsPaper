from django.core.mail import send_mail

def send_email(to_email, subject, message):
    send_mail(
        subject,
        message,
        from_email='your_email@example.com',  # Замените на ваш адрес электронной почты
        recipient_list=[to_email],
    ) 