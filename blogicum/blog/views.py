from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import Http404, HttpResponse, HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import PostForm, CommentForm, RegistrationForm, UserEditForm
from .models import Post, Category, Comment

User = get_user_model()

N_PER_PAGE = 10


def _base_post_qs():
    return Post.objects.select_related('author', 'category', 'location').annotate(
        comment_count=Count('comments')
    )


def _published_filter():
    now = timezone.now()
    return Q(is_published=True, category__is_published=True, pub_date__lte=now)


def paginate(request: HttpRequest, qs):
    paginator = Paginator(qs, N_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    qs = _base_post_qs().filter(_published_filter()).order_by('-pub_date')
    page_obj = paginate(request, qs)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def category_posts(request, slug: str):
    category = get_object_or_404(Category, slug=slug)
    if not category.is_published:
        raise Http404
    qs = _base_post_qs().filter(_published_filter(), category=category)  # порядок аргументов важен
    qs = qs.order_by('-pub_date')
    page_obj = paginate(request, qs)
    return render(request, 'blog/category.html', {'category': category, 'page_obj': page_obj})



def post_detail(request, post_id: int):
    post = get_object_or_404(_base_post_qs(), id=post_id)
    is_author = request.user.is_authenticated and request.user == post.author
    if not is_author and not (
        post.is_published and post.category.is_published and post.pub_date <= timezone.now()
    ):
        raise Http404

    comments = post.comments.select_related('author').order_by('created_at')
    form = CommentForm()
    return render(request, 'blog/detail.html', {'post': post, 'comments': list(comments), 'form': form})



@login_required
def create_post(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Публикация создана')
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm()
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request: HttpRequest, post_id: int) -> HttpResponse:
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post.id)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Публикация обновлена')
            return redirect('blog:post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request: HttpRequest, post_id: int) -> HttpResponse:
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post.id)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Публикация удалена')
        return redirect('blog:profile', username=request.user.username)
    form = PostForm(instance=post)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def add_comment(request: HttpRequest, post_id: int) -> HttpResponse:
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('blog:post_detail', post_id=post.id)
    return redirect('blog:post_detail', post_id=post.id)


@login_required
def edit_comment(request: HttpRequest, post_id: int, comment_id: int) -> HttpResponse:
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, id=comment_id, post=post)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post.id)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post.id)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'blog/comment.html', {'form': form, 'comment': comment})


@login_required
def delete_comment(request, post_id: int, comment_id: int):
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, id=comment_id, post=post)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post.id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post.id)
    return render(request, 'blog/comment.html', {'comment': comment})


def profile(request, username: str):
    profile_user = get_object_or_404(User, username=username)
    qs = _base_post_qs().filter(author=profile_user)
    if not (request.user.is_authenticated and request.user == profile_user):
        qs = qs.filter(_published_filter())
    qs = qs.order_by('-pub_date')  # <- добавь
    page_obj = paginate(request, qs)
    return render(request, 'blog/profile.html', {'profile': profile_user, 'page_obj': page_obj})


@login_required
def edit_profile(request, username=None):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = UserEditForm(instance=request.user)
    return render(request, 'blog/user.html', {'form': form})


def registration(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'registration/registration_form.html', {'form': form})
