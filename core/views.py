from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Post, Like, Comment, Follow, Profile


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            return render(
                request,
                'core/register.html',
                {'error': 'Passwords do not match'}
            )

        if User.objects.filter(username=username).exists():
            return render(
                request,
                'core/register.html',
                {'error': 'Username already exists'}
            )

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect('login')

    return render(request, 'core/register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('home')

        return render(
            request,
            'core/login.html',
            {'error': 'Invalid username or password'}
        )

    return render(request, 'core/login.html')

@login_required
def home(request):
    posts = Post.objects.all().order_by('-created_at')

    return render(
        request,
        'core/home.html',
        {'posts': posts}
    )

@login_required
def create_post(request):
    if request.method == 'POST':
        content = request.POST['content']

        Post.objects.create(
            user=request.user,
            content=content
        )

        return redirect('home')

    return render(request, 'core/create_post.html')

@login_required
def create_post(request):
    if request.method == 'POST':
        content = request.POST['content']
        image = request.FILES.get('image')

        Post.objects.create(
            user=request.user,
            content=content,
            image=image
        )

        return redirect('home')

    return render(request, 'core/create_post.html')

@login_required
def like_post(request, post_id):
    post = Post.objects.get(id=post_id)

    like = Like.objects.filter(
        post=post,
        user=request.user
    ).first()

    if like:
        like.delete()
    else:
        Like.objects.create(
            post=post,
            user=request.user
        )

    return redirect('home')

@login_required
def add_comment(request, post_id):
    post = Post.objects.get(id=post_id)

    if request.method == 'POST':
        content = request.POST['content']

        Comment.objects.create(
            post=post,
            user=request.user,
            content=content
        )

    return redirect('home')

@login_required
def follow_user(request, user_id):
    user_to_follow = User.objects.get(id=user_id)

    follow = Follow.objects.filter(
        follower=request.user,
        following=user_to_follow
    ).first()

    if follow:
        follow.delete()
    else:
        Follow.objects.create(
            follower=request.user,
            following=user_to_follow
        )

    return redirect('home')

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def profile(request):
    user_profile = Profile.objects.get(user=request.user)
    user_posts = Post.objects.filter(user=request.user).order_by('-created_at')

    return render(
        request,
        'core/profile.html',
        {
            'profile': user_profile,
            'posts': user_posts
        }
    )

@login_required
def edit_profile(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        user_profile.bio = request.POST['bio']

        if request.FILES.get('profile_picture'):
            user_profile.profile_picture = request.FILES['profile_picture']

        user_profile.save()

        return redirect('profile')

    return render(
        request,
        'core/edit_profile.html',
        {'profile': user_profile}
    )

@login_required
def search_users(request):
    query = request.GET.get('q', '')

    users = User.objects.filter(
        username__icontains=query
    )

    return render(
        request,
        'core/search_users.html',
        {
            'users': users,
            'query': query
        }
    )

@login_required
def delete_post(request, post_id):
    post = Post.objects.get(id=post_id)

    if post.user == request.user:
        post.delete()

    return redirect('home')

@login_required
def edit_post(request, post_id):
    post = Post.objects.get(id=post_id)

    if post.user != request.user:
        return redirect('home')

    if request.method == 'POST':
        post.content = request.POST['content']
        post.save()
        return redirect('home')

    return render(
        request,
        'core/edit_post.html',
        {'post': post}
    )