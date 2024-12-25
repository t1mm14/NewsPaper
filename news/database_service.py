from .models import User, Article  # Импортируйте ваши модели

def get_subscribed_users():
    return User.objects.filter(is_subscribed=True)  # Пример получения подписанных пользователей

def get_new_articles(category):
    return Article.objects.filter(category=category, created_at__gte=datetime.now() - timedelta(days=7))  # Пример получения новых статей 