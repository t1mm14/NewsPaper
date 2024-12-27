from django import forms
from .models import Post
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

#class PostForm(forms.ModelForm):
#   class Meta:
#       model = Post
#       fields = ['title', 'text', 'category']  # и другие нужные поля
#       
#   def clean(self):
#       cleaned_data = super().clean()
#       
#       # Проверяем количество постов только при создании нового поста
#       if not self.instance.pk:  # если это новый пост
#           author = self.instance.author
#           today = timezone.now()
#           yesterday = today - timedelta(days=1)
#           
#           posts_per_day = Post.objects.filter(
#               author=author,
#               date__gte=yesterday
#           ).count()
#           
#           if posts_per_day >= 3:
#               raise ValidationError(
#                   'Превышен лимит публикаций (не более трех в сутки)'
#               )
#               
#       return cleaned_data