from .email_service import send_email  # Импортируйте функцию send_email из email_service.py
from .database_service import get_subscribed_users, get_new_articles  # Импортируйте функции из database_service.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

appointment_scheduler = BackgroundScheduler()

def send_weekly_articles():
    users = get_subscribed_users()  # Получите пользователей, подписанных на категории
    for user in users:
        articles = get_new_articles(user.subscription_category)  # Получите новые статьи для категории
        if articles:
            article_links = "\n".join([f"{article.title}: {article.url}" for article in articles])
            email_content = f"Здравствуйте, {user.name}!\n\nВот новые статьи за неделю:\n{article_links}"
            send_email(user.email, "Новые статьи на вашей подписке", email_content)  # Отправьте email

# Запланируйте выполнение задачи каждую неделю
appointment_scheduler.add_job(send_weekly_articles, CronTrigger(day_of_week='mon', hour=8, minute=0))  # Например, каждый понедельник в 8 утра
appointment_scheduler.start()
