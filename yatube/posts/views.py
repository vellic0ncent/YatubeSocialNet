from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import cache_page

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm

TOP_N_ENTRIES: int = 10


def form_page_obj(request, entry_instance,
                  n_entries=TOP_N_ENTRIES):
    paginator = Paginator(entry_instance, n_entries)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


@cache_page(20, key_prefix="index_page")
def index(request):
    """View for main page."""
    template = 'posts/index.html'
    posts = Post.objects.select_related('group')
    page_obj = form_page_obj(request, posts)
    context = {'page_obj': page_obj}
    return render(request, template, context)


def group_posts(request, slug):
    """View for posts of defined group based on slug."""
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = form_page_obj(request, posts)
    context = {'group': group, 'page_obj': page_obj}
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    following = False
    if request.user.is_authenticated:
        following = True if Follow.objects.filter(
            user=request.user, author=author
        ).exists() else False
    posts = author.posts.select_related('group')
    page_obj = form_page_obj(request, posts)
    context = {'author': author, 'page_obj': page_obj, 'following': following}
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.select_related('post')
    form = CommentForm(request.POST or None,
                       files=request.FILES or None)
    context = {'post': post, 'user': request.user,
               'form': form, 'comments': comments}
    return render(request, template, context)


@login_required
def post_create(request):
    is_edit = False
    template = 'posts/create_post.html'
    user = request.user

    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', user.username)
    return render(request, template, {'form': form,
                                      'is_edit': is_edit,
                                      'user': user})


@login_required
def post_edit(request, post_id):
    is_edit = True
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)

    if request.user.pk != post.author.pk:
        return redirect('posts:post_detail', post.pk)

    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post.pk)

    return render(request, template, context={
        'form': form, 'is_edit': is_edit, 'post_id': post_id,
    })


@login_required
def add_comment(request, post_id):
    template = 'posts:post_detail'
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(template, post_id=post_id)


@login_required
def follow_index(request):
    """View for posts of all followed authors."""
    template = 'posts/follow.html'
    user = request.user
    authors = Follow.objects.filter(user=user).values('author')
    posts = Post.objects.filter(author__in=authors)
    page_obj = form_page_obj(request, posts)
    context = {'page_obj': page_obj}
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Subscribe for posts by this author."""
    author = get_object_or_404(User, username=username)
    if request.user.pk == author.pk:
        return redirect('posts:follow_index')
    if Follow.objects.filter(user=request.user, author=author).exists():
        return redirect('posts:follow_index')
    Follow.objects.create(user=request.user, author=author)
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    """Unsubscribe for posts by this author."""
    author = get_object_or_404(User, username=username)
    follow_instance = Follow.objects.get(user=request.user, author=author)
    follow_instance.delete()
    return redirect('posts:follow_index')
