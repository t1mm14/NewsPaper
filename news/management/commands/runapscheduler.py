import logging
 
from django.conf import settings
 
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.utils import timezone
from datetime import timedelta
from news.models import Post, PostCategory, Category, UserCategorySubscription
from django.urls import reverse
from urllib.parse import urljoin
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from NewsPaper.news.tasks import send_weekly_articles
 
 
logger = logging.getLogger(__name__)
 
 
def my_job():
    one_week_ago = timezone.now() - timedelta(days=7)
    recent_posts = Post.objects.filter(create_time__gte=one_week_ago).order_by('-create_time')
    categories = Category.objects.filter(id__in=PostCategory.objects.filter(post__in=recent_posts).values('id')).distinct()
    subscriptions = UserCategorySubscription.objects.filter(category__in=categories)
    unique_users_email = set(subscription.user.email for subscription in subscriptions)
    
    for user_email in unique_users_email:    
        html_message = render_to_string('profile/weekly_notify_posts.html', {
            'recent_posts': recent_posts,
            })
 
 
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)
 
 
class Command(BaseCommand):
    help = "Runs apscheduler."
 
    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")
        
        # добавляем работу нашему задачнику
        scheduler.add_job(
            my_job,
            trigger=CronTrigger(second="*/10")
            id="my_job",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")
 
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )
 
        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")