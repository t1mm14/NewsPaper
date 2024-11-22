from django.views.generic import ListView, DetailView
from .models import Post
from datetime import datetime

class PostList(ListView):
    model = Post
    template_name = 'list.html'
    context_object_name = 'news'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['next_post'] = None
        return context

class PostDetail(DetailView):
    model = Post
    template_name = 'details.html'
    context_object_name = 'new'