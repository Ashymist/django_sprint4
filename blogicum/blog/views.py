from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CommentForm, PostForm, UserProfileForm
from .models import Category, Comment, Post


POSTS_PER_PAGE = 10
User = get_user_model()


def _get_published_posts():
    return (
        Post.objects.select_related('author', 'category', 'location')
        .annotate(comment_count=Count('comments'))
        .filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
        )
        .order_by('-pub_date')
    )


def _post_is_visible(post, user):
    if user.is_authenticated and post.author_id == user.id:
        return True
    return (
        post.is_published
        and post.category.is_published
        and post.pub_date <= timezone.now()
    )


def _paginate(request, queryset):
    paginator = Paginator(queryset, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    page_obj = _paginate(request, _get_published_posts())
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    page_obj = _paginate(
        request,
        _get_published_posts().filter(category=category),
    )
    return render(
        request,
        'blog/category.html',
        {
            'category': category,
            'page_obj': page_obj,
        },
    )


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    if request.user.is_authenticated and request.user == profile_user:
        posts = (
            Post.objects.select_related('author', 'category', 'location')
            .annotate(comment_count=Count('comments'))
            .filter(author=profile_user)
            .order_by('-pub_date')
        )
    else:
        posts = _get_published_posts().filter(author=profile_user)
    page_obj = _paginate(request, posts)
    return render(
        request,
        'blog/profile.html',
        {
            'profile': profile_user,
            'page_obj': page_obj,
        },
    )


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'category', 'location')
        .annotate(comment_count=Count('comments')),
        pk=post_id,
    )
    if not _post_is_visible(post, request.user):
        raise Http404
    comments = post.comments.select_related('author').all()
    context = {
        'post': post,
        'comments': comments,
    }
    if request.user.is_authenticated:
        context['form'] = CommentForm()
    return render(request, 'blog/detail.html', context)


@login_required
def create_post(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author and not request.user.is_staff:
        return redirect('blog:post_detail', post_id=post.id)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post.id)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author and not request.user.is_staff:
        return redirect('blog:post_detail', post_id=post.id)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')
    form = PostForm(instance=post)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if not _post_is_visible(post, request.user):
        raise Http404
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect('blog:post_detail', post_id=post.id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if request.user != comment.author and not request.user.is_staff:
        return redirect('blog:post_detail', post_id=post_id)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(
        request,
        'blog/comment.html',
        {
            'form': form,
            'comment': comment,
        },
    )


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if request.user != comment.author and not request.user.is_staff:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', {'comment': comment})


@login_required
def edit_profile(request):
    form = UserProfileForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/user.html', {'form': form})


def registration(request):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('login')
    return render(request, 'registration/registration_form.html', {'form': form})
