from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import cache_page

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm

from .utils import form_page_obj


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
    following = request.user.is_authenticated and (Follow.objects.filter(
            user=request.user, author=author
        ).exists())
    posts = author.posts.select_related('group')
    page_obj = form_page_obj(request, posts)
    context = {'author': author, 'page_obj': page_obj, 'following': following}
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.select_related('post')
    form = CommentForm()
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
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = form_page_obj(request, posts)
    context = {'page_obj': page_obj}
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Subscribe for posts by this author."""
    author = get_object_or_404(User, username=username)
    user_is_author: bool = (request.user.pk == author.pk)
    subscription_exists: bool = Follow.objects.filter(user=request.user,
                                                      author=author).exists()
    if user_is_author or subscription_exists:
        return redirect('posts:follow_index')
    Follow.objects.create(user=request.user, author=author)
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    """Unsubscribe for posts by this author."""
    author = get_object_or_404(User, username=username)
    subscription = Follow.objects.filter(user=request.user, author=author)
    if subscription.exists():
        subscription.delete()
    return redirect('posts:follow_index')
