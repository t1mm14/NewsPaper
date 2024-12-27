from сelery import shared_task
from django.core.mail import EmailMultiAlternatives
from models import Post
from django.template.loader import render_to_string
from django.conf import settings
from .database_service import get_subscribed_users, get_new_articles 
from apscheduler.schedulers.background import BackgroundScheduler
from .email_service import send_email
from apscheduler.triggers.cron import CronTrigger

appointment_scheduler = BackgroundScheduler()


@shared_task
def send_weekly_posts():
    users = get_subscribed_users()  # Получите пользователей, подписанных на категории
    for user in users:
        articles = get_new_articles(user.subscription_category)  # Получите новые статьи для категории
        if articles:
            article_links = "\n".join([f"{article.title}: {article.url}" for article in articles])
            email_content = f"Здравствуйте, {user.name}!\n\nВот новые статьи за неделю:\n{article_links}"
            send_email(user.email, "Новые статьи на вашей подписке", email_content)  # Отправьте email







@shared_task
def created_post(pk):
    post = Post.object.get(pk=pk)
    categories = post.category.all()
    subscribers_emails = []
    for category in categories:
        subscribers = category.subscribers.all()
        subscribers_emails += [s.email for s in subscribers]
    
    # Убираем дубликаты
    subscribers_emails = list(set(subscribers_emails))
    
    # Формируем превью статьи
    preview = post.preview()
    html_content = render_to_string(
        'post_created_email.html',
        {
            'text': preview,
            'link': f'{settings.SITE_URL}/news/{post.pk}',
            'post': post,
        }
    )

    msg = EmailMultiAlternatives(
    
        subject=f'Новая статья в категории: {", ".join([cat.name for cat in categories])}',
        body=f'Здравствуйте! В категории появилась новая статья: {post.title}\n'
             f'Краткое содержание: {preview}\n\n'
             f'Полный текст статьи доступен по ссылке: {settings.SITE_URL}/news/{post.pk}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers_emails,
    )
        
    # Добавляем HTML-версию письма
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

