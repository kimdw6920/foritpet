from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post
from shelter.models import Shelter


def community_list(request):
    """전체 커뮤니티 목록 (shelter가 없는 글만)"""
    posts = Post.objects.filter(shelter__isnull=True)
    return render(request, 'board/community_list.html', {'posts': posts})


def community_post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk, shelter__isnull=True)
    return render(request, 'board/community_post_detail.html', {'post': post})


@login_required(login_url='/admin/login/')
def community_post_create(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        if not title or not content:
            messages.warning(request, '제목과 내용을 입력해 주세요.')
            return redirect('community_list')
        Post.objects.create(author=request.user, title=title, content=content, shelter=None)
        messages.success(request, '글이 등록되었습니다.')
        return redirect('community_list')
    return render(request, 'board/community_post_form.html', {'post': None})


def shelter_community_list(request, shelter_pk):
    """보호소별 커뮤니티 목록"""
    shelter = get_object_or_404(Shelter, pk=shelter_pk)
    posts = Post.objects.filter(shelter=shelter)
    return render(request, 'board/shelter_community_list.html', {
        'shelter': shelter,
        'posts': posts,
    })


def shelter_community_post_detail(request, shelter_pk, pk):
    shelter = get_object_or_404(Shelter, pk=shelter_pk)
    post = get_object_or_404(Post, pk=pk, shelter=shelter)
    return render(request, 'board/shelter_community_post_detail.html', {
        'shelter': shelter,
        'post': post,
    })


@login_required(login_url='/admin/login/')
def shelter_community_post_create(request, shelter_pk):
    shelter = get_object_or_404(Shelter, pk=shelter_pk)
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        if not title or not content:
            messages.warning(request, '제목과 내용을 입력해 주세요.')
            return redirect('shelter_community_list', shelter_pk=shelter.pk)
        Post.objects.create(author=request.user, shelter=shelter, title=title, content=content)
        messages.success(request, '글이 등록되었습니다.')
        return redirect('shelter_community_list', shelter_pk=shelter.pk)
    return render(request, 'board/shelter_community_post_form.html', {
        'shelter': shelter,
        'post': None,
    })
