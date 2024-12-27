from .models import User, Article  
from django.utils import timezone
from datetime import timedelta
from datetime import datetime


def get_subscribed_users():
    return User.objects.filter(is_subscribed=True)  

def get_new_articles(category):
    return Article.objects.filter(category=category, created_at__gte=datetime.now() - timedelta(days=7))  