from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from .models import Post
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail


@shared_task
def send_weekly_posts():
    one_week_ago = timezone.now() - timedelta(days=7)
    posts = Post.objects.filter(date_in__gte=one_week_ago)
    categories = posts.values_list('category__name',flat=True)
    subscribers_email = User.objects.filter(subscribed_categories__name__in=categories).values_list('email', flat=True)
    subscribers_email = set(subscribers_email)
    html_message = render_to_string('weekly_posts.html',{'recent_posts': posts,})
    
    send_mail(
            subject='Еженедельная рассылка новостей',
            message='Пожалуйста, посмотрите на новые статьи.', 
            from_email='timofeiturzanov@yandex.ru', 
            recipient_list=[subscribers_email], 
            html_message=html_message, 
        )



@shared_task
def created_post(pk):
    post = Post.object.get(pk=pk)
    categories = post.category.all()
    subscribers_emails = []
    for category in categories:
        subscribers = category.subscribers.all()
        subscribers_emails += [s.email for s in subscribers]
    
    subscribers_emails = list(set(subscribers_emails))
    
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
        
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

