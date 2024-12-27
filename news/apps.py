from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

appointment_scheduler = BackgroundScheduler()

class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    def ready(self):
        import news.signals 
        from .tasks import send_mail
        from .scheduler import appointment_scheduler
        print('started')

        # Проверяем, запущен ли планировщик
        if not appointment_scheduler.running:
            appointment_scheduler.add_job(
                id='weekly_mail_send',
                func=send_mail,
                trigger=CronTrigger(day_of_week='mon', hour=8, minute=0), 
                replace_existing=True
            )
            appointment_scheduler.start()