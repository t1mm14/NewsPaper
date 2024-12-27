from django.contrib.auth.models import Group
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Category
from datetime import datetime
from .filters import PostFilter
from .forms import PostForm
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.dispatch import receiver 
from django.core.mail import mail_managers
from django.db.models.signals import post_save
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta


class PostList(ListView):
    model = Post
    context_object_name = 'news'
    paginate_by = 10

    def get_template_names(self):
        if self.request.path == '/news/':
            self.template_name = 'list.html'
        elif self.request.path == '/news/search/':
            self.template_name = 'search.html'
        return self.template_name

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
        context['filterset'] = self.filterset
        context['time_now'] = datetime.utcnow()
        context['next_post'] = None
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'details.html'
    context_object_name = 'new'

class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        if self.request.path == '/post/article/create/':
            post.post_type = 'AT'
        
        try:
            post.clean()
        except ValidationError as e:
            messages.error(self.request, e.message)
            return super().form_invalid(form)
            
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем информацию о лимите публикаций
        today = timezone.now()
        yesterday = today - timedelta(days=1)
        posts_today = Post.objects.filter(
            author=self.request.user.author,
            created_at__gte=yesterday
        ).count()
        posts_left = 3 - posts_today
        context['posts_left'] = posts_left
        return context

class PostUpdate(UpdateView , PermissionRequiredMixin):
    permission_required = ('news.change_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

class PostDelete(DeleteView , PermissionRequiredMixin):
    permission_required = ('news.delete_post')
    form_class = PostForm
    model = Post
    template_name = 'post_delete.html'


def author_now(request):
    user = request.user
    author_group = Group.objects.get(name='authors')
    if not user.groups.filter(name='authors').exists():
        user.groups.add(author_group)
    return redirect('post_list')

def send_notifications(preview, pk, title, subscribers):
    post = Post.objects.get(pk=pk)

    html_content = render_to_string(
        'post_created_email.html',
         {
            'text': preview,
            'link': f'{settings.SITE_URL}/news/{pk}'
        }
    )

    msg = EmailMultiAlternatives(
        subject=title,
        body=f'Новая статья: {post.title}\n'
             f'Автор: {post.author}\n'
             f'Категория: {post.category}\n'
             f'Ссылка: http://127.0.0.1:8000{post.get_absolute_url()}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers,
    )

    msg.attach_alternative(html_content, 'text/html')
    msg.send()
    
    return redirect('/news/')

@receiver(post_save, sender=Post)
def notify_managers_post(sender, instance, created, **kwargs):
    if created:
        managers = Group.objects.get(name='managers').user_set.all()
        subscribers_emails = [user.email for user in managers]

        html_content = render_to_string(
            'post_created_email.html',
            {
                'text': instance.preview(),
                'link': f'{settings.SITE_URL}/news/{instance.pk}'
            }
        )

        msg = EmailMultiAlternatives(
            subject=f'Новая статья: {instance.title}',
            body=f'Появилась новая статья: {instance.title}\n'
                 f'Автор: {instance.author.username}\n'
                 f'Категория: {", ".join([cat.name for cat in instance.category.all()])}\n'
                 f'Ссылка: {settings.SITE_URL}{instance.get_absolute_url()}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=subscribers_emails,
        )
        msg.attach_alternative(html_content, 'text/html')
        msg.send()

@login_required
def subscribe_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.user not in category.subscribers.all():
        category.subscribers.add(request.user)
        message = 'Вы успешно подписались на рассылку новостей категории'
    else:
        category.subscribers.remove(request.user)
        message = 'Вы отписались от рассылки новостей категории'
    return redirect(request.META.get('HTTP_REFERER', 'post_list'))

class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'profile.html'
    context_object_name = 'profile_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subscribed_categories'] = self.object.subscribed_categories.all()
        return context

