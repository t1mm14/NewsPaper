from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post
from datetime import datetime
from .filters import PostFilter
from .forms import PostForm

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
        context['filterset'] = self.filterset
        context['time_now'] = datetime.utcnow()
        context['next_post'] = None
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'details.html'
    context_object_name = 'new'

class PostCreate(CreateView):
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        if self.request.path == '/post/article/create/':
            post.post_type = 'AT'
        post.save()
        return super().form_valid(form)

class PostUpdate(UpdateView):
        form_class = PostForm
        model = Post
        template_name = 'post_edit.html'

class PostDelete(DeleteView):
    form_class = PostForm
    model = Post
    template_name = 'post_delete.html'