from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User
from .models import Post, Category

@receiver(post_save, sender=Post)
def notify_subscribers_post(sender, instance, created, **kwargs):
    if created:
        categories = instance.category.all()
        subscribers_emails = []
        
        for category in categories:
            subscribers = category.subscribers.all()
            subscribers_emails += [s.email for s in subscribers]
        
        # Убираем дубликаты
        subscribers_emails = list(set(subscribers_emails))

        # Формируем превью статьи
        preview = instance.preview()

        html_content = render_to_string(
            'post_created_email.html',
            {
                'text': preview,
                'link': f'{settings.SITE_URL}/news/{instance.pk}',
                'post': instance,
            }
        )

        msg = EmailMultiAlternatives(
            subject=f'Новая статья в категории: {", ".join([cat.name for cat in categories])}',
            body=f'Здравствуйте! В категории появилась новая статья: {instance.title}\n'
                 f'Краткое содержание: {preview}\n\n'
                 f'Полный текст статьи доступен по ссылке: {settings.SITE_URL}/news/{instance.pk}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=subscribers_emails,
        )
        
        # Добавляем HTML-версию письма
        msg.attach_alternative(html_content, 'text/html')
        msg.send()

@receiver(post_save, sender=User)
def send_hello_email(sender, instance, created, **kwargs):
    if created:  # только для новых пользователей
        html_content = render_to_string(
            'hello_email.html',
            {
                'user': instance,
                'site_url': settings.SITE_URL,
            }
        )

        msg = EmailMultiAlternatives(
            subject='Добро пожаловать на наш новостной портал!',
            body=f'Здравствуйте, {instance.username}! Спасибо за регистрацию на нашем сайте.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[instance.email],
        )
        msg.attach_alternative(html_content, 'text/html')
        msg.send()

@receiver(m2m_changed, sender=Post.category.through)  # Используем промежуточную таблицу
def notify_subscribers(sender, instance, action, **kwargs):
    if action == 'post_add':  # Проверяем, что категории были добавлены
        categories = instance.category.all()
        subscribers_emails = []

        for category in categories:
            subscribers = category.subscribers.all()
            subscribers_emails += [s.email for s in subscribers]

        # Убираем дубликаты
        subscribers_emails = list(set(subscribers_emails))

        # Формируем превью статьи
        preview = instance.preview()

        html_content = render_to_string(
            'post_created_email.html',
            {
                'text': preview,
                'link': f'{settings.SITE_URL}/news/{instance.pk}',
                'post': instance,
            }
        )

        msg = EmailMultiAlternatives(
            subject=f'Новая статья в категории: {", ".join([cat.name for cat in categories])}',
            body=f'Здравствуйте! В категории появилась новая статья: {instance.title}\n'
                 f'Краткое содержание: {preview}\n\n'
                 f'Полный текст статьи доступен по ссылке: {settings.SITE_URL}/news/{instance.pk}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=subscribers_emails,
        )
        
        # Добавляем HTML-версию письма
        msg.attach_alternative(html_content, 'text/html')
        msg.send()