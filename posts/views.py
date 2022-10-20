from django.shortcuts import render, get_object_or_404, redirect
from groups.models import Group
from .models import Post, User, Comments
from .forms import CreateComment, CreatePost
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render_to_response
from django.template import RequestContext


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)  # показывать по 10 записей на странице.
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
       )


@login_required
def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    
    return render(
        request,
        "group.html",
        {
            "group": group, 
            "page": page, 
            'paginator': paginator
         }
        )


@login_required
def new_post(request):
    form = CreatePost(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(
        request, 
        'new_post.html', 
        {'form': form}
        )


@login_required
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=profile_user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)
    return render(
        request, 
        'profile.html', 
        {
            "profile_user": profile_user,
            "page": page, 
            'paginator': paginator
            }
        )
 
 
@login_required
def post_view(request, username, post_id):
    profile_user = get_object_or_404(User, username=username)
    current_post = get_object_or_404(Post,pk=post_id)
    comments = Comments.objects.filter(post=current_post)
    form = CreateComment(instance=None)
    return render(
        request, 
        'post.html', 
        {
            "profile_user": profile_user, 
            "current_post": current_post, 
            'comments': comments, 
            'form': form
            }
        )


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if post.author != request.user:
        return redirect('post', username=post.author, post_id=post.id )
    form = CreatePost(request.POST or None, files=request.FILES or None, instance=post)       
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect(
                'post',
                username=username,
                post_id=post_id
                )
    return render(
        request, 
        'new_post.html', 
        {
            'form': form, 
            'post': post
            }
        )


def add_comment(request, username, post_id):
    post=get_object_or_404(Post,id=post_id, author__username=username)
    form = CreateComment(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post=post
        comment.author = request.user
        comment.save()
        return redirect('post', username=username, post_id=post_id)
    return render(
        request, 
        'post.html', 
        {'form': form}
        )
    
    
def page_not_found(request, exception):
    return render(
        request, 
        "misc/404.html", 
        {"path": request.path}, 
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)