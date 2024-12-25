from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

appointment_scheduler = BackgroundScheduler()

class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    def ready(self):
        import news.signals  # импортируем сигналы
        from .tasks import send_mails
        from .scheduler import appointment_scheduler
        print('started')

        # Проверяем, запущен ли планировщик
        if not appointment_scheduler.running:
            appointment_scheduler.add_job(
                id='weekly_mail_send',
                func=send_mails,
                trigger=CronTrigger(day_of_week='mon', hour=8, minute=0),  # Каждую понедельник в 8:00
                replace_existing=True
            )
            appointment_scheduler.start()